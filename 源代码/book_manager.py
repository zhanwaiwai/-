"""图书管理。"""
import math
from mongodb_connect import get_database

def validate(book):
    for field in ("isbn", "title", "author", "publisher", "category"):
        if not isinstance(book.get(field), str) or not book[field].strip():
            raise ValueError(f"{field} 必须为非空字符串")
    if len(book["isbn"]) != 13 or not book["isbn"].isdigit():
        raise ValueError("ISBN 必须为13位数字")
    for field in ("price", "rating"):
        value = book.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{field} 必须为有限数值")
    if book["price"] < 0 or not 0 <= book["rating"] <= 5:
        raise ValueError("价格不能为负数，评分范围为0—5")
    if type(book.get("stock")) is not int or book["stock"] < 0:
        raise ValueError("库存必须为非负整数")
    if not isinstance(book.get("tags", []), list) or any(not isinstance(x, str) for x in book.get("tags", [])):
        raise ValueError("tags 必须为字符串数组")
    if type(book.get("borrow_count", 0)) is not int or book.get("borrow_count", 0) < 0:
        raise ValueError("借阅次数必须为非负整数")

def add_book(book):
    validate(book)
    return get_database().books.insert_one(dict(book)).inserted_id

def add_books(books):
    if not books: raise ValueError("批量数据不能为空")
    for book in books: validate(book)
    return len(get_database().books.insert_many([dict(x) for x in books]).inserted_ids)

def search_books(filters=None, page=1, page_size=10):
    if page < 1 or not 1 <= page_size <= 100: raise ValueError("分页参数无效")
    return list(get_database().books.find(filters or {}).sort("isbn", 1).skip((page-1)*page_size).limit(page_size))

def find_book(isbn):
    return get_database().books.find_one({"isbn": isbn})

def ranking(n=5):
    if not 1 <= n <= 100: raise ValueError("N范围为1—100")
    return list(get_database().books.find({}, {"_id": 0, "title": 1, "rating": 1, "borrow_count": 1}).sort([("rating", -1), ("isbn", 1)]).limit(n))

def change_stock(isbn, delta):
    if type(delta) is not int: raise ValueError("库存增减值必须为整数")
    query = {"isbn": isbn}
    if delta < 0: query["stock"] = {"$gte": -delta}
    return get_database().books.update_one(query, {"$inc": {"stock": delta}}).modified_count

def delete_book(isbn):
    return get_database().books.delete_one({"isbn": isbn}).deleted_count

def delete_books(isbns):
    if not isbns: raise ValueError("必须指定待删除ISBN清单")
    return get_database().books.delete_many({"isbn": {"$in": list(isbns)}}).deleted_count
