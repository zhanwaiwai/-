"""统一连接；通过环境变量配置，不把密码写进源码。"""
import os
from pymongo import MongoClient

URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/")
DATABASE = os.getenv("MONGODB_DATABASE", "library")
_client = None

def get_database():
    global _client
    if _client is None:
        _client = MongoClient(URI, serverSelectionTimeoutMS=5000, tz_aware=True)
    _client.admin.command("ping")
    return _client[DATABASE]

def close_connection():
    global _client
    if _client is not None:
        _client.close()
        _client = None
