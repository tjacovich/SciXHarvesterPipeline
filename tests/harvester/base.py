import requests_mock


class MockGetRecord(requests_mock.MockerCore):
    """
    Thin wrapper around the MockADSWSAPI class specficically for the Solr
    Query end point.
    """

    def __init__(self, **kwargs):
        requests_mock.MockerCore.__init__(self)
        self.kwargs = kwargs
        with open('tests/data/GetRecord_data.xml', 'r+') as f:
             response_text = f.read()
        self.url='https://export.arxiv.org/oai2?verb=GetRecord&identifier=oai%3AarXiv.org%3A2107.10460'

        self.register_uri('GET', self.url, text=response_text)
    
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

class MockListRecords(requests_mock.MockerCore):
    """
    Thin wrapper around the MockADSWSAPI class specficically for the Solr
    Query end point.
    """
    def __init__(self, **kwargs):
        requests_mock.MockerCore.__init__(self)
        self.kwargs = kwargs
        self.url='https://export.arxiv.org/oai2'
        self.possible_params = ['?metadataPrefix=oai_dc&verb=ListRecords&from=2023-03-07', '?verb=ListRecords&resumptionToken=6511260%7C1001', '?verb=ListRecords&resumptionToken=6511260%7C2001']

        for i in range(0, len(self.possible_params)):
            self.register_uri('GET', self.url+str(self.possible_params[i]), text=self.callback(i))
    
    def callback(self, i):
        with open('tests/data/ListRecords_data_{}.xml'.format(i), 'r+') as f:
             response_text = f.read()
        return response_text

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

class MockListIdentifiers(requests_mock.MockerCore):
    """
    Thin wrapper around the MockADSWSAPI class specficically for the Solr
    Query end point.
    """

    def __init__(self, **kwargs):
        requests_mock.MockerCore.__init__(self)
        self.kwargs = kwargs
        with open('tests/data/ListIdentifiers_data.xml', 'r+') as f:
             response_text = f.read()
        self.url='https://export.arxiv.org/oai2?metadataPrefix=oai_dc&verb=ListIdentifiers&from=2023-03-07'

        self.register_uri('GET', self.url, text=response_text)
    
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()