"""流水使用时间序列集合；可变归还状态保存在普通集合 borrow_state。
演示版单进程使用。跨集合写入采用补偿；不宣称支持跨集合事务。
"""
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from mongodb_connect import get_database

def register(card, isbn):
    db = get_database()
    if not db.readers.find_one({"card_no": card}): raise ValueError("读者不存在")
    result = db.books.update_one({"isbn": isbn, "stock": {"$gt": 0}}, {"$inc": {"stock": -1, "borrow_count": 1}})
    if result.modified_count != 1: raise ValueError("图书不存在或库存不足")
    record = {"_id": ObjectId(), "reader_card": card, "book_isbn": isbn,
              "borrow_date": datetime.now(timezone.utc), "status": "借出"}
    try:
        db.borrow_state.insert_one(dict(record))
        db.borrow_logs.insert_one(dict(record))
    except Exception:
        db.borrow_state.delete_one({"_id": record["_id"]})
        db.books.update_one({"isbn": isbn}, {"$inc": {"stock": 1, "borrow_count": -1}})
        raise
    return record["_id"]

def return_book(log_id):
    db = get_database()
    oid = ObjectId(log_id) if isinstance(log_id, str) else log_id
    record = db.borrow_state.find_one({"_id": oid})
    if not record: raise ValueError("借阅记录不存在")
    result = db.borrow_state.update_many({"_id": oid, "status": {"$in": ["借出", "逾期"]}, "return_date": None},
        {"$set": {"status": "已归还", "return_date": datetime.now(timezone.utc)}})
    if result.modified_count:
        stock = db.books.update_one({"isbn": record["book_isbn"]}, {"$inc": {"stock": 1}})
        if not stock.matched_count:
            db.borrow_state.update_one({"_id": oid}, {"$set": {"status": record["status"]}, "$unset": {"return_date": ""}})
            raise ValueError("图书已删除，归还操作已撤销")
    return result.modified_count

def overdue(days=30, now=None):
    if days < 1: raise ValueError("借期必须为正数")
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=days)
    return list(get_database().borrow_state.find({"return_date": None, "$or": [{"status": "逾期"},
        {"status": "借出", "borrow_date": {"$lt": cutoff}}]}).sort("borrow_date", 1))
