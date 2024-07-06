
import pymongo
import os

def connect_mongodb():
    client = pymongo.MongoClient(
        host = os.getenv('MONGODB_HOST'),
        username=os.getenv('MONGODB_USER'),
        password=os.getenv('MONGODB_PWD'),
    )
    return client