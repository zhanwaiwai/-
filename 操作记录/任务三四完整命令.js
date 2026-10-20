// 在完成初始化后按顺序运行，仅用于一次性实验；重复运行会再次修改数据。
// 按编号逐条执行。D1使用实际删除记录的业务键，D3动态获取当前库_id；I1的重复插入报错11000是预期结果。
use("library");
// 环境
db.version()
// 结果见 results.json 的 环境

// 集合设计
db.getCollectionInfos()
// 结果见 results.json 的 集合设计

// 导入计数
db.books.countDocuments({}); db.readers.countDocuments({}); db.borrow_logs.countDocuments({});
// 结果见 results.json 的 导入计数

// Q1
db.books.find({"price": {"$gt": 80}}).toArray()
// 结果见 results.json 的 Q1

// Q2
db.books.find({"stock": {"$lt": 10}}).toArray()
// 结果见 results.json 的 Q2

// Q3
db.books.find({"isbn": {"$eq": "9787115428028"}}).toArray()
// 结果见 results.json 的 Q3

// Q4
db.readers.find({"email": {"$eq": null}}).toArray()
// 结果见 results.json 的 Q4

// Q5
db.books.find({"publisher": {"$ne": "人民邮电出版社"}}).toArray()
// 结果见 results.json 的 Q5

// Q6
db.books.find({"category": {"$in": ["计算机", "经济管理"]}}).toArray()
// 结果见 results.json 的 Q6

// Q7
db.books.find({"$and": [{"rating": {"$gt": 4.0}}, {"category": "计算机"}]}).toArray()
// 结果见 results.json 的 Q7

// Q8
db.books.find({"$or": [{"rating": {"$lt": 3.5}}, {"stock": 0}]}).toArray()
// 结果见 results.json 的 Q8

// Q9
db.books.find({"title": {"$regex": "Python"}}).toArray()
// 结果见 results.json 的 Q9

// Q10
db.books.find({"tags": {"$all": ["编程", "入门"]}}).toArray()
// 结果见 results.json 的 Q10

// Q11
db.books.find({"tags": {"$size": 3}}).toArray()
// 结果见 results.json 的 Q11

// Q12
db.books.find({"tags": {"$exists": true}}).toArray()
// 结果见 results.json 的 Q12

// Q13
db.books.find({"_id": {"$type": "string"}}).toArray()
// 结果见 results.json 的 Q13

// Q14
db.books.find({}).sort({rating:-1,isbn:1}).limit(5).toArray()
// 结果见 results.json 的 Q14

// Q15
db.books.find({}, {_id:0,title:1,price:1,rating:1}).toArray()
// 结果见 results.json 的 Q15

// Q16
db.books.distinct("category")
// 结果见 results.json 的 Q16

// U1
db.books.updateOne({"isbn": "9787115428028"},{"$inc": {"stock": -5}})
// 结果见 results.json 的 U1

// U2
db.books.updateMany({"category": "计算机"},{"$mul": {"price": 0.9}})
// 结果见 results.json 的 U2

// U3
db.books.updateOne({"isbn": "9787115428028"},{"$currentDate": {"updated_at": true}})
// 结果见 results.json 的 U3

// U4
db.books.updateOne({"isbn": "9787115428028"},{"$unset": {"tags": ""}})
// 结果见 results.json 的 U4

// D1
db.borrow_logs.deleteOne({status:{$eq:"已归还"},reader_card:"R20240010",book_isbn:"9787020042033",borrow_date:ISODate("2023-01-08T15:27:00+08:00")})
// 结果见 results.json 的 D1

// D2预览
db.borrow_logs.find({"status": "逾期", "return_date": null}).toArray()
// 结果见 results.json 的 D2预览

// D2
db.borrow_logs.deleteMany({"status": "逾期", "return_date": null})
// 结果见 results.json 的 D2

// D3
db.readers.replaceOne({"_id": db.readers.findOne({card_no:"R20240001"})._id},{"_id": db.readers.findOne({card_no:"R20240001"})._id, "card_no": "R20240001", "name": "张明", "college": "计算机学院", "email": "zhangming.updated@example.edu", "phone": "13800138000", "level": "教师", "register_date": ISODate("2024-08-31T16:00:00Z"), "fav_categories": ["计算机", "文学"]})
// 结果见 results.json 的 D3

// A1
db.books.aggregate([{"$group": {"_id": "$category", "book_count": {"$sum": 1}, "avg_rating": {"$avg": "$rating"}}}, {"$sort": {"_id": 1}}]).toArray()
// 结果见 results.json 的 A1

// A2
db.books.aggregate([{"$group": {"_id": "$publisher", "count": {"$sum": 1}}}, {"$group": {"_id": null, "top5": {"$topN": {"n": 5, "sortBy": {"count": -1, "_id": 1}, "output": {"publisher": "$_id", "count": "$count"}}}}}]).toArray()
// 结果见 results.json 的 A2

// A3
db.books.aggregate([{"$sortByCount": "$category"}, {"$sort": {"count": -1, "_id": 1}}, {"$limit": 1}]).toArray()
// 结果见 results.json 的 A3

// A4
db.books.aggregate([{"$sort": {"rating": -1, "isbn": 1}}, {"$limit": 3}, {"$project": {"_id": 0, "title": 1, "borrow_count": 1}}]).toArray()
// 结果见 results.json 的 A4

// A5
db.books.aggregate([{"$project": {"_id": 0, "title": 1, "sales": {"$round": [{"$multiply": ["$price", "$borrow_count"]}, 2]}}}]).toArray()
// 结果见 results.json 的 A5

// A6
db.borrow_logs.aggregate([{"$group": {"_id": {"$year": {"date": "$borrow_date", "timezone": "Asia/Shanghai"}}, "count": {"$sum": 1}, "sample_date": {"$min": "$borrow_date"}}}, {"$project": {"_id": 0, "year": {"$dateToString": {"format": "%Y年", "date": "$sample_date", "timezone": "Asia/Shanghai"}}, "count": 1}}, {"$sort": {"year": 1}}]).toArray()
// 结果见 results.json 的 A6

// A7
db.borrow_logs.aggregate([{"$group": {"_id": "$reader_card", "count": {"$sum": 1}}}, {"$sort": {"count": -1, "_id": 1}}, {"$limit": 5}]).toArray()
// 结果见 results.json 的 A7

// A8
db.borrow_logs.aggregate([{"$lookup": {"from": "readers", "localField": "reader_card", "foreignField": "card_no", "as": "reader"}}, {"$unwind": "$reader"}, {"$group": {"_id": "$reader.college", "count": {"$sum": 1}}}, {"$sort": {"count": -1, "_id": 1}}]).toArray()
// 结果见 results.json 的 A8

// A9
db.books.aggregate([{"$group": {"_id": "$category", "book_count": {"$sum": 1}, "avg_rating": {"$avg": "$rating"}}}, {"$sort": {"_id": 1}}, {"$merge": {"into": "category_stats", "on": "_id", "whenMatched": "replace", "whenNotMatched": "insert"}}]).toArray()
// 结果见 results.json 的 A9

// 索引清单
db.books.getIndexes()
// 结果见 results.json 的 索引清单

// I1重复验证
db.books.insertOne({"isbn": "9787115428028", "title": "Python编程：从入门到实践", "author": "埃里克·马瑟斯", "publisher": "人民邮电出版社", "category": "计算机", "price": 80.10000000000001, "stock": 10, "rating": 4.6, "publish_date": ISODate("2023-02-28T16:00:00Z"), "borrow_count": 127, "updated_at": ISODate("2026-10-15T11:51:54.977Z"), "_id": ObjectId("6ad0be5a31b32aa1404249ed")})
// 结果见 results.json 的 I1重复验证

// 无索引扫描
db.books.find({"isbn": "9787115428028"}).hint({"$natural": 1}).explain("executionStats")
// 结果见 results.json 的 无索引扫描

// 唯一索引扫描
db.books.find({"isbn": "9787115428028"}).hint("isbn_1").explain("executionStats")
// 结果见 results.json 的 唯一索引扫描

// 更新后复核
// Compass以此快照核对，不使用更新前Q1/Q2/Q7/Q14
// 结果见 results.json 的 更新后复核