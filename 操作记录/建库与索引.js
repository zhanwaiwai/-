// 在mongosh中，从提交包根目录运行load("操作记录/建库与索引.js")。
// 仅用于空库；与python main.py --init二选一。
db = db.getSiblingDB("library");
if(db.books.countDocuments({}) || db.readers.countDocuments({}) || db.borrow_logs.countDocuments({})) throw Error("已有数据，拒绝覆盖");
db.createCollection("books");
db.createCollection("readers");
db.createCollection("category_stats");
db.createCollection("borrow_state");
db.createCollection("book_logs",{capped:true,size:1048576,max:1000});
db.createCollection("borrow_logs",{timeseries:{timeField:"borrow_date",granularity:"hours"},expireAfterSeconds:63072000});
db.createView("book_in_stock","books",[{$match:{stock:{$gt:0}}}]);
const fs=require("fs");
const books=EJSON.parse(fs.readFileSync("数据/books.txt","utf8").replace(/^\uFEFF/,""));
printjson(db.books.insertOne(books[0]));printjson(db.books.insertMany(books.slice(1)));
const readers=EJSON.parse(fs.readFileSync("数据/readers.txt","utf8").replace(/^\uFEFF/,""));
printjson(db.readers.insertMany(readers));
const logs=EJSON.parse(fs.readFileSync("数据/borrow_logs.txt","utf8").replace(/^\uFEFF/,""));
logs.forEach(x=>{if(!x._id)x._id=new ObjectId()});
printjson(db.borrow_logs.insertMany(logs));printjson(db.borrow_state.insertMany(logs));
printjson(db.books.createIndex({isbn:1},{unique:true}));
printjson(db.books.createIndex({title:1}));
printjson(db.books.createIndex({category:1}));
printjson(db.books.createIndex({tags:1}));
printjson(db.books.createIndex({category:1,price:1}));
printjson(db.readers.createIndex({card_no:1},{unique:true}));
printjson(db.getCollectionInfos());
printjson({books:db.books.countDocuments({}),readers:db.readers.countDocuments({}),borrow_logs:db.borrow_logs.countDocuments({})});
