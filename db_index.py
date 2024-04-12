from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['xml_data']
db.items.create_index([("g:id", 1)])