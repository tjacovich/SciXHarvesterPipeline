from harvester.base.OAIHarvester import OAIHarvester as OAI
from harvester.utils import get_schema
import time
import logging as logger
from harvester import db
from adsingestp.parsers import arxiv
import re
import uuid
from datetime import datetime

MAX_RETRIES = 5

def arxiv_harvesting(app, job_request, config, producer):
    datestamp = datetime.now()
    resumptionToken = job_request["task_args"].get("resumptionToken")
    harvester = ArXiV_Harvester(config.get("ARXIV_OAI_URL"), daterange=datestamp, resumptionToken=resumptionToken)
    harvester_output_schema = get_schema(app, app.schema_client, app.config.get('HARVESTER_OUTPUT_SCHEMA'))
    for record in harvester:
        record_id = uuid.uuid4()
        file_path = "/{}/{}".format(datestamp, record_id)
        
        etag = app.s3_methods.write_object_s3(file_bytes=bytes(record), bucket=config.get('ARXIV_S3_BUCKET'), object_name=file_path)
        if etag:
            s3_key = file_path
            produce = db.write_harvester_record(app, record_id, record, datestamp, s3_key, etag, job_request.get("task"))

            if produce:
                #placeholder code for producing to harvester output topic.
                producer_message = {"record_id": record_id, "record_xml": record, "source": job_request.get("task")}
                producer.produce(topic=config.get('HARVESTER_OUTPUT_TOPIC'), value=producer_message, value_schema=config.get('HARVESTER_OUTPUT_SCHEMA'))
        else:
            return "Error"

    return "Success"

class ArXiV_Harvester(OAI):
    def __init__(self, harvest_url, daterange, resumptionToken):
        self.url = harvest_url
        self.params = {'metadataPrefix': 'oai_dc'}
        self.daterange = None
        self.raw_xml = ''
        self.parsed_records = self.harvest_arxiv(harvest_url, daterange, resumptionToken)

    @staticmethod

    def harvest_arxiv(self, daterange, resumptionToken = None):
        """
        daterange: (str) date with value given as YYYY-MM-DD
        resumptionToken: (str) value returned by previous API call for paging.

        return: (json) ArXiV API response
        """

        success = False
        retries = 0

        while success != True:
            """
            This loop sends the relevant request to the ArXiV API and checks to make sure we aren't receiving any flow control responses.
            If we are it waits the specified amount of time before proceeding. If we repeatedly hit 
            """
            if not resumptionToken:
                self.params['from'] = daterange
                self.daterange = daterange
            
            else:
                #specifying any other query params besides the verb with the resumptionToken will result in an error.
                self.params = {'resumptionToken': resumptionToken}

            try:
                raw_response = self.ListRecords(self.url, self.params)
                raw_records = raw_response.content
                success = True
            except  Exception as e:
                if raw_response.status_code == 503  and retries < MAX_RETRIES:
                    retries += 1 
                    sleep_time = 1
                    time.sleep(sleep_time)
                else:
                    logger.exception("Failed to Harvest ArXiV records for daterange: {}".format(daterange))
                    raise e

            self.parsed_records = arxiv.ArxivParser.parse(raw_records)

    def __next__(self):
        try:
            record = next(self.parsed_records)
        except:
            try:
                resumptionToken = self.extract_resumptionToken(self.raw_xml)
            except:
                logger.debug("Harvesting has finished")
            if resumptionToken:
                self.harvest_arxiv(daterange=self.daterange, resumptionToken=resumptionToken)
                record = next(self.parsed_records)  
        
        yield record

    @staticmethod
    def extract_resumptionToken(raw_xml):
        arxiv_parser = arxiv.MultiArxivParser()
        token_text = arxiv_parser.get_chunks(raw_xml, r"<resumptionToken", r"</resumptionToken>")
        pattern = re.compile(r"[0-9]+\|[0-9]+")
        pattern.search(token_text)[0]


