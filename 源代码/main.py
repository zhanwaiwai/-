"""运行 python main.py；初始化 python main.py --init。"""
import argparse
import re
from pathlib import Path
from bson import json_util
from pymongo.errors import PyMongoError
from mongodb_connect import get_database, close_connection
import book_manager as books
import reader_manager as readers
import borrow_manager as borrow
import stat_manager as stats

def show(rows):
    if not rows:
        print("无匹配结果")
        return
    print(json_util.dumps(rows, ensure_ascii=False, indent=2))

def initialize():
    db = get_database()
    if any(db[name].count_documents({}) for name in ("books", "readers", "borrow_logs", "borrow_state")):
        raise ValueError("目标库已有数据，拒绝覆盖。请使用新建空库进行初始化。")
    existing = db.list_collection_names()
    for name in ("books", "readers", "category_stats", "borrow_state"):
        if name not in existing: db.create_collection(name)
    if "borrow_logs" not in existing:
        db.create_collection("borrow_logs", timeseries={"timeField": "borrow_date", "granularity": "hours"}, expireAfterSeconds=63072000)
    if "book_logs" not in existing: db.create_collection("book_logs", capped=True, size=1048576, max=1000)
    if "book_in_stock" not in existing:
        db.create_collection("book_in_stock", viewOn="books", pipeline=[{"$match": {"stock": {"$gt": 0}}}])
    base = Path(__file__).resolve().parent.parent / "数据"
    for name in ("books", "readers", "borrow_logs"):
        data = json_util.loads((base / (name+".txt")).read_text(encoding="utf-8-sig"))
        if name == "books":
            db[name].insert_one(data[0]); db[name].insert_many(data[1:])
        else: db[name].insert_many(data)
        if name == "borrow_logs": db.borrow_state.insert_many([dict(x) for x in data])
        print(f"{name}: 插入 {len(data)} 条")
    db.books.create_index("isbn", unique=True)
    for field in ("title", "category", "tags"): db.books.create_index(field)
    db.books.create_index([("category", 1), ("price", 1)])
    db.readers.create_index("card_no", unique=True)
    print("初始化完成。注意：两年TTL会清理过期历史流水；固定数据复现实验请按说明暂停TTL监视器。")

MENU = """
图书情报检索与统计平台
1 条件检索  2 评分排行  3 分类统计  4 年度趋势  5 畅销榜
6 库存调整  7 删除图书  8 读者列表  9 学院统计  10 等级分布
11 借阅登记  12 归还处理  13 逾期查询  14 新增图书
15 批量新增  16 保存读者  17 删除读者  18 批量删除图书
19 月度趋势  0 退出"""

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    try:
        db = get_database()
        print("数据库连接成功：" + db.name)
        if args.init: initialize(); return
        for name in sorted(db.list_collection_names()):
            if not name.startswith("system."): print(f"{name}: {db[name].count_documents({})} 条")
        while True:
            print(MENU)
            try:
                choice = input("请选择：").strip()
                if choice == "0": break
                if choice == "1":
                    key = input("书名/作者/ISBN关键词（可空）：").strip()
                    filt = {"$or": [{k: {"$regex": re.escape(key), "$options": "i"}} for k in ("title", "author", "isbn")]} if key else {}
                    extra = input('附加MongoDB条件JSON（回车跳过）：').strip()
                    if extra:
                        parsed = json_util.loads(extra)
                        if not isinstance(parsed, dict): raise ValueError("条件必须为JSON对象")
                        filt = {"$and": [filt, parsed]}
                    page = int(input("页码（默认1）：") or "1")
                    show(books.search_books(filt, page))
                elif choice == "2": show(books.ranking())
                elif choice == "3": show(stats.categories())
                elif choice == "4": show(stats.trend())
                elif choice == "5": show(stats.popular())
                elif choice == "6": print("修改文档数：", books.change_stock(input("ISBN："), int(input("增减量："))))
                elif choice == "7":
                    isbn = input("ISBN：")
                    if input("输入 DELETE 确认：") == "DELETE": print("删除文档数：", books.delete_book(isbn))
                elif choice == "8": show(readers.readers())
                elif choice == "9": show(readers.distribution("college"))
                elif choice == "10": show(readers.distribution("level"))
                elif choice == "11": print("新增借阅1条，库存修改1条，记录ID：", borrow.register(input("借阅证号："), input("ISBN：")))
                elif choice == "12":
                    n = borrow.return_book(input("借阅记录ID：")); print(f"归还记录数：{n}；库存修改数：{n}")
                elif choice == "13": show(borrow.overdue())
                elif choice == "14": print("新增文档数：1；ID：", books.add_book(json_util.loads(input("图书JSON："))))
                elif choice == "15": print("新增文档数：", books.add_books(json_util.loads(Path(input("JSON数组文件路径：")).read_text(encoding="utf-8-sig"))))
                elif choice == "16": print("变更文档数：", readers.save_reader(json_util.loads(input("读者JSON："))))
                elif choice == "17":
                    card = input("借阅证号：")
                    if input("输入 DELETE 确认：") == "DELETE": print("删除文档数：", readers.delete_reader(card))
                elif choice == "18":
                    isbns = [s.strip() for s in input("ISBN清单，逗号分隔：").split(",") if s.strip()]
                    if input("输入 DELETE 确认：") == "DELETE": print("删除文档数：", books.delete_books(isbns))
                elif choice == "19": show(stats.trend(True))
                else: print("无效选项")
            except (ValueError, TypeError, KeyError, OSError, PyMongoError) as exc:
                print("操作失败：", exc)
    except (ValueError, PyMongoError) as exc:
        print("启动失败：", exc)
    except (EOFError, KeyboardInterrupt):
        print("输入结束")
    finally:
        close_connection(); print("数据库连接已关闭")

if __name__ == "__main__": run()
