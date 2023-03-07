from harvester.base.OAIHarvester import OAIHarvester as OAI
from tests.harvester.base import MockListRecords, MockGetRecord, MockListIdentifiers
from unittest import TestCase
import requests_mock
import pytest

class test_OAI_harvesting(TestCase):
    def test_OAI_GetRecord(self):
        with MockGetRecord():
            get_records = OAI.GetRecord(url='https://export.arxiv.org/oai2', params={'identifier':'oai:arXiv.org:2107.10460'})
        with open('tests/data/GetRecord_data.xml', 'r+') as f:
            response_text = f.read()
        self.assertEqual(get_records.text, str(response_text))    

    def test_OAI_ListRecords(self):
        with MockListRecords():
            list_records = OAI.ListRecords(url='https://export.arxiv.org/oai2', params={'from':'2023-03-07', 'metadataPrefix': 'oai_dc'})
            with open('tests/data/ListRecords_data_0.xml', 'r+') as f:
                response_text = f.read()            
            self.assertEqual(list_records.text, response_text)
            list_records = OAI.ListRecords(url='https://export.arxiv.org/oai2', params={'resumptionToken':'6511260|1001'})
            with open('tests/data/ListRecords_data_1.xml', 'r+') as f:
                response_text = f.read()            
            self.assertEqual(list_records.text, response_text)
            list_records = OAI.ListRecords(url='https://export.arxiv.org/oai2', params={'resumptionToken':'6511260|2001'})
            with open('tests/data/ListRecords_data_2.xml', 'r+') as f:
                response_text = f.read()            
            self.assertEqual(list_records.text, response_text)
            with pytest.raises(requests_mock.exceptions.NoMockAddress):
                list_records = OAI.ListRecords(url='https://export.arxiv.org/oai2', params={'resumptionToken':'6511260|3001'})

    def test_OAI_ListIdentifiers(self):
        with MockListIdentifiers():
            list_identifiers = OAI.ListIdentifiers(url='https://export.arxiv.org/oai2', params={'from':'2023-03-07', 'metadataPrefix': 'oai_dc'})
        with open('tests/data/ListIdentifiers_data.xml', 'r+') as f:
            response_text = f.read()
        self.assertEqual(list_identifiers.text, str(response_text))
