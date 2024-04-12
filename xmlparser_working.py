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

    def startElement(self, tag, attributes):
        self.current_data = tag
        self.current_value = ""

        # Handle the applink element with its attributes
        if tag == 'applink':
            applink_data = dict(attributes)
            self.applinks.append(applink_data)

    def endElement(self, tag):
        if tag == 'item':
            if self.applinks:
                # Add the list of applinks to the item data before inserting into MongoDB
                self.item_data['applinks'] = self.applinks
                self.applinks = []  # Reset the applinks for the next item

            # Insert the item into MongoDB
            self.collection.insert_one(self.item_data)
            self.item_data = {}  # Reset item_data for the next item
        elif tag == 'shipping':
            # Nested shipping data is already handled by characters() and startElement()
            pass
        else:
            # Remove namespace URI if present
            tag = tag.split('}', 1)[-1]
            # Set the text content for the current tag
            self.item_data[tag] = self.current_value.strip()
            self.current_data = ""

    def characters(self, content):
        if self.current_data:
            self.current_value += content

    def endDocument(self):
        # This is called at the end of the document
        # Here we can ensure any final processing required
        pass


def parse_and_store(xml_file):
    # Disable loading external DTDs (DOCTYPEs)
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    handler = ItemHandler()
    parser.setContentHandler(handler)
    parser.parse(xml_file)


parse_and_store('fb.xml')
