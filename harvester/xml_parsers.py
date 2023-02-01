from xml.dom import pulldom
import logging as logger

class arxiv_xml_parsers(object):
    @staticmethod
    def parse_list_records():
        return True
    
    def parse_list_identifiers():
        return True
    
    def parse_get_record():
        return True

class Split_ListRecords(arxiv_xml_parsers):
    def __init__(self, raw_xml):
        self.pull_parser = pulldom.parse(raw_xml)
        self.resumptionToken = None

    def __next__(self):
        for record in self.parse_list_records(self.pull_parser):
            try:
                split_record = ListRecord(record.get('identifier'), record.get('datestamp'), record.get('contents'))
            except:
                try:
                    yield {'resumptionToken': self.resumptionToken}
                except Exception as e:
                    logger.error("Generator failed with exception: {}".format(e))
                    
            yield split_record 

class ListRecord(object):
    def __init__(self, identifier, datestamp, contents):
        self.identifier = identifier
        self.datestamp = datestamp
        self.contents = contents