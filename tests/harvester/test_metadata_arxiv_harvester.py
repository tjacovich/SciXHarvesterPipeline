from harvester.metadata.arxiv_harvester import ArXiV_Harvester
from tests.harvester.base import MockListRecords
from unittest import TestCase
import pickle
import requests
import pytest

class test_ArXiV_Harvester(TestCase):
    def test_arxiv_harvester_from(self):
        with MockListRecords():
            arxiv_harvester = ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange='2023-03-07', resumptionToken=None)
            with open('tests/data/ListRecords_data_0.xml', 'r+') as f:
                response_text = f.read()    
            self.assertEqual(arxiv_harvester.raw_xml, response_text)
    
    def test_arxiv_harvester_resumptionToken(self):
        with MockListRecords():
            arxiv_harvester = ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange=None, resumptionToken='6511260|1001')
            with open('tests/data/ListRecords_data_1.xml', 'r+') as f:
                response_text = f.read()    
            self.assertEqual(arxiv_harvester.raw_xml, response_text)

    def test_arxiv_harvester_resumptionToken_retry_after(self):
        with MockListRecords(error_503=True):
            with pytest.raises(requests.exceptions.Timeout):
                ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange=None, resumptionToken='6511260|1001')
        
    
    def test_arxiv_harvester_generator(self):
        with MockListRecords():
            arxiv_harvester = ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange='2023-03-07', resumptionToken=None)
            harvested_records = []
            for record in arxiv_harvester:
                harvested_records.append(record)
            with open('tests/data/parsed_records.pkl', 'rb') as f:
                test_records = pickle.load(f)
            self.assertEqual(2265, len(harvested_records))
            self.assertEqual(harvested_records, test_records)

