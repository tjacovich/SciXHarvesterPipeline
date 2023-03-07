from harvester.base.OAIHarvester import OAIHarvester as OAI
from tests.harvester.base import MockGetRecord, MockListRecords, MockListIdentifiers
from unittest import TestCase

class test_OAI_harvesting(TestCase):
    def test_OAI_GetRecord(self):
        with MockGetRecord():
            get_records = OAI.GetRecord(url='https://export.arxiv.org/oai2', params={'identifier':'oai:arXiv.org:2107.10460'})
            self.assertEqual(get_records, get_records)
    
    def test_OAI_ListRecords(self):
        with MockListRecords():
            list_records = OAI.ListRecords(url='https://export.arxiv.org/oai2', params={'from':'2023-03-01'})
            self.assertEqual(list_records, list_records)

    def test_OAI_ListIdentifiers(self):
        with MockListIdentifiers():
            list_identifiers = OAI.ListIdentifiers(url='https://export.arxiv.org/oai2', params={'from':'2023-03-01'})
            self.assertEqual(list_identifiers, list_identifiers)
