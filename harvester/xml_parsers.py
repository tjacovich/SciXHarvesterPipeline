class arxiv_xml_parsers(object):
    @staticmethod
    def parse_get_records():
        return True

class Split_GetRecords(arxiv_xml_parsers):
    def __init__(self, raw_xml):
        self.raw_xml = raw_xml

    def __next__():
        return True

class GetRecord(object):
    def __init__(self, identifier, datestamp, contents):
        self.identifier = identifier
        self.datestamp = datestamp
        self.contents = contents