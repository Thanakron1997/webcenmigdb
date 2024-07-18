
import pymongo
import os
import hashlib 
from dotenv import load_dotenv
load_dotenv()

def connect_mongodb():
    client = pymongo.MongoClient(
        host = os.getenv('MONGODB_HOST'),
        username=os.getenv('MONGODB_USER'),
        password=os.getenv('MONGODB_PWD'),
    )
    return client

def getApiKey():
    client = connect_mongodb()
    db = client['api']
    mycol = db["api_key"]
    dquery = mycol.find_one({}, {'_id': 0})
    result = hashlib.sha256(dquery['api_key'].encode())
    return result.hexdigest()