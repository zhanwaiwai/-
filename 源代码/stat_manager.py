"""聚合统计，日期统一按 Asia/Shanghai。"""
from mongodb_connect import get_database

def categories():
    return list(get_database().books.aggregate([
        {"$group": {"_id": "$category", "stock_total": {"$sum": "$stock"},
                    "avg_price": {"$avg": "$price"}, "book_count": {"$sum": 1},
                    "max_stock": {"$max": "$stock"}, "min_stock": {"$min": "$stock"}}},
        {"$sort": {"stock_total": -1, "_id": 1}}]))

def trend(monthly=False):
    fmt = "%Y-%m" if monthly else "%Y年"
    return list(get_database().borrow_logs.aggregate([
        {"$group": {"_id": {"$dateToString": {"format": fmt, "date": "$borrow_date", "timezone": "Asia/Shanghai"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}]))

def popular(n=5):
    if not 1 <= n <= 100: raise ValueError("N范围为1—100")
    return list(get_database().books.aggregate([{"$sort": {"borrow_count": -1, "isbn": 1}}, {"$limit": n},
        {"$project": {"_id": 0, "title": 1, "borrow_count": 1}}]))
