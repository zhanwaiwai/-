"""读者信息管理与分布统计。"""
from mongodb_connect import get_database

def readers(filters=None):
    return list(get_database().readers.find(filters or {}).sort("card_no", 1))

def save_reader(reader):
    if not all(isinstance(reader.get(k), str) and reader[k].strip() for k in ("card_no", "name", "college")):
        raise ValueError("借阅证号、姓名和学院不能为空")
    if reader.get("level", "普通") not in ("普通", "高级", "教师"):
        raise ValueError("借阅等级无效")
    result = get_database().readers.update_one({"card_no": reader["card_no"]}, {"$set": dict(reader)}, upsert=True)
    return result.modified_count + int(result.upserted_id is not None)

def delete_reader(card):
    db = get_database()
    if db.borrow_state.count_documents({"reader_card": card, "return_date": None, "status": {"$in": ["借出", "逾期"]}}):
        raise ValueError("该读者尚有未归还图书")
    return db.readers.delete_one({"card_no": card}).deleted_count

def distribution(field="college"):
    if field not in ("college", "level"): raise ValueError("仅支持学院和等级统计")
    col = get_database().readers
    return [{field: value, "count": col.count_documents({field: value})} for value in sorted(col.distinct(field))]
