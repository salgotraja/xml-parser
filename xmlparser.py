import xml.sax
from pymongo import MongoClient


class ItemHandler(xml.sax.ContentHandler):
    def __init__(self, uri='mongodb://localhost:27017/', dbname='xml_data', colname='items'):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]
        self.collection = self.db[colname]
        self.current_data = ""
        self.current_value = ""
        self.item_data = {}
        self.applinks = []
        self.is_within_shipping = False

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
        if tag == 'shipping':
            self.is_within_shipping = False
        elif self.is_within_shipping:
            tag = tag.split('}', 1)[-1]
            self.item_data['shipping'][tag] = self.current_value.strip()
        elif tag == 'item':
            if self.applinks:
                self.item_data['applinks'] = self.applinks
                self.applinks = []

            self.collection.insert_one(self.item_data)
            self.item_data = {}
        else:
            tag = tag.split('}', 1)[-1]
            self.item_data[tag] = self.current_value.strip()

        self.current_data = ""
        self.current_value = ""

    def characters(self, content):
        if self.current_data:
            self.current_value += content

    def endDocument(self):
        pass


def parse_and_store(xml_file):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    handler = ItemHandler()
    parser.setContentHandler(handler)
    parser.parse(xml_file)


parse_and_store('fb.xml')