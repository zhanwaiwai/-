// 在新建隔离实验实例、启用访问控制前逐条执行。
db=db.getSiblingDB("library");
db.createUser({user:"libReader",pwd:passwordPrompt(),roles:[{role:"read",db:"library"}]});
db.createUser({user:"libWriter",pwd:passwordPrompt(),roles:[{role:"readWrite",db:"library"},{role:"dbAdmin",db:"library"}]});
// 关闭本实验mongod，然后使用相同dbpath加--auth重新启动。
// mongosh --host 127.0.0.1 --port 27017 --username libReader --authenticationDatabase library --password
// db=db.getSiblingDB("library");
// db.books.countDocuments({}); // 20
// db.books.insertOne({isbn:"AUTH-TEST",title:"权限测试"}); // Unauthorized code 13
// 以libWriter登录后可插入；验证后deleteOne删除AUTH-TEST。
