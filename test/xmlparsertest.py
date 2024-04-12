import unittest
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_mongo_db(self):
        with MongoDbContainer() as mongo:
            uri = mongo.get_connection_url()
            client = MongoClient(uri)
            db = client.test

            # Perform actions on the database
            db.my_collection.insert_one({"x": 1})
            self.assertEqual(db.my_collection.find_one()["x"], 1)


if __name__ == '__main__':
    unittest.main()
