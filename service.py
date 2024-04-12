from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['xml_data']
collection = db['items']


@app.route('/items', methods=['GET'])
def get_items():
    gid = request.args.get('g:id', default=None)
    gender = request.args.get('g:gender', default=None)

    query = {}
    if gid:
        query['g:id'] = gid
    if gender:
        query['g:gender'] = gender

    items_cursor = collection.find(query)

    items_json = dumps(items_cursor)

    return items_json, 200


if __name__ == '__main__':
    app.run(debug=True)
