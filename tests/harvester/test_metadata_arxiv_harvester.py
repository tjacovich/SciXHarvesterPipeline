from harvester.metadata.arxiv_harvester import ArXiV_Harvester
from tests.harvester.base import MockListRecords
from unittest import TestCase

class test_ArXiV_Harvester(TestCase):
    def test_arxiv_harvester_from(self):
        with MockListRecords():
            arxiv_harvester = ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange='2023-03-07', resumptionToken=None)
    def test_arxiv_harvester_resumptionToken(self):
        with MockListRecords():
            arxiv_harvester = ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange=None, resumptionToken='6511260|1001')
    def test_arxiv_harvester_generator(self):
        with MockListRecords():
            arxiv_harvester = ArXiV_Harvester(harvest_url='https://export.arxiv.org/oai2', daterange='2023-03-07', resumptionToken=None)
            for record in arxiv_harvester:
                pass