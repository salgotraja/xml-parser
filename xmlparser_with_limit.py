import os
import logging
import xml.sax
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer


class ItemHandler(xml.sax.ContentHandler):
    def __init__(self, uri='mongodb://localhost:27017/', dbname='xml_data', colname='items', max_records=1000):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.collection = self.db[colname]
        self.current_data = ""
        self.current_value = ""
        self.item_data = {}
        self.applinks = []
        self.is_within_shipping = False
        self.record_count = 0
        self.max_records = max_records

    def startElement(self, tag, attributes):
        self.current_data = tag
        self.current_value = ""

        if tag == 'shipping':
            self.is_within_shipping = True
            self.item_data['shipping'] = {}
        elif self.is_within_shipping:
            pass
        elif tag == 'applink':
            applink_data = dict(attributes)
            self.applinks.append(applink_data)

    def endElement(self, tag):
        if tag == 'item':
            if self.applinks:
                self.item_data['applinks'] = self.applinks
                self.applinks = []

            self.collection.insert_one(self.item_data)
            self.item_data = {}
            self.record_count += 1

            if self.record_count >= self.max_records:
                raise xml.sax.SAXException("Maximum number of records reached", None)

    def characters(self, content):
        if self.current_data:
            self.current_value += content

    def endDocument(self):
        pass


def parse_and_store(xml_file, uri, dbname, colname, max_records=1000, batch_size=100):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    handler = ItemHandler(uri, dbname, colname, max_records)
    parser.setContentHandler(handler)

    try:
        parser.parse(xml_file)
    except xml.sax.SAXException as e:
        if str(e) == "Maximum number of records reached":
            logging.info("Reached the maximum number of records to process.")
        else:
            logging.error("XML parsing error: %s", e)
            raise  # Re-raise exceptions that are not related to the record limit
    except Exception as e:
        logging.error("Unexpected error during parsing: %s", e)
        raise


def main():
    logging.basicConfig(level=logging.INFO)

    xml_file = os.getenv('XML_FILE', 'fb.xml')
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGODB_DATABASE', 'xml_data')
    collection_name = os.getenv('MONGODB_COLLECTION', 'items')

    with MongoDbContainer() as mongodb:
        mongo_uri = mongodb.get_connection_url()
        parse_and_store(xml_file, mongo_uri, db_name, collection_name)


if __name__ == "__main__":
    main()
