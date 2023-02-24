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
    """
    Main harvesting routine for arxiv metadata. 
    
    job_request: (json) task message passed to Harvester input topic.
    config: (json) The imported configuration of the Harvester app.
    producer: The harvester kafka producer instance

    return: (str) The final state of the harvesting process.
    """
    datestamp = datetime.now()
    resumptionToken = job_request["task_args"].get("resumptionToken")
    daterange = job_request["task_args"].get("daterange")
    harvester_output_schema = get_schema(app, app.schema_client, app.config.get('HARVESTER_OUTPUT_SCHEMA'))

    harvester = ArXiV_Harvester(config.get("ARXIV_OAI_URL"), daterange=daterange, resumptionToken=resumptionToken)
    
    for record in harvester:
        #Assign ID to new record
        record_id = uuid.uuid4()
        #Generate filepath for S3
        file_path = "/{}/{}".format(datestamp, record_id)
        #write record to S3
        etag = app.s3_methods.write_object_s3(file_bytes=bytes(record), bucket=config.get('ARXIV_S3_BUCKET'), object_name=file_path)
        if etag:
            s3_key = file_path
            produce = db.write_harvester_record(app, record_id, record, datestamp, s3_key, etag, job_request.get("task"))

            if produce:
                producer_message = {"record_id": record_id, "record_xml": record, "source": job_request.get("task")}
                producer.produce(topic=config.get('HARVESTER_OUTPUT_TOPIC'), value=producer_message, value_schema=harvester_output_schema)
        else:
            return "Error"

    return "Success"

class ArXiV_Harvester(OAI):
    def __init__(self, harvest_url, daterange, resumptionToken):
        """
        Initialization of harvesting class.

        url: (str) The OAI harvesting url
        params: (json) The required requests parameters
        daterange: (str) A specified harvesting date range.
        parsed_records: (array) Calls harvest method to produce an array of records accessible from the __next__ method.
        """
        self.url = harvest_url
        self.params = {'metadataPrefix': 'oai_dc'}
        self.daterange = daterange
        self.raw_xml = None
        self.parsed_records = self.harvest_arxiv(harvest_url, resumptionToken)

    def harvest_arxiv(self, resumptionToken = None):
        """
        daterange: (str) date with value given as YYYY-MM-DD
        resumptionToken: (str) value returned by previous API call for paging.

        return: (json) ArXiV API response
        """

        success = False
        retries = 0

        while success != True:
            """
            This loop:
            1. Sends the relevant request to the ArXiV API
            2. Checks to make sure we aren't receiving any flow control responses.
            3. If we are it waits the specified amount of time before proceeding. 
            4. If we repeatedly hit 503 or any other error, we stop.
            """
            if not resumptionToken:
                self.params['from'] = self.daterange
            
            else:
                #specifying any other query params besides the verb with the resumptionToken will result in an error.
                self.params = {'resumptionToken': resumptionToken}

            try:
                raw_response = self.ListRecords(self.url, self.params)
                self.raw_xml = raw_response.content
                success = True
            except  Exception as e:
                """
                Still need to write the code that extracts the retry-after time from the response.
                """
                if raw_response.status_code == 503  and retries < MAX_RETRIES:
                    retries += 1 
                    sleep_time = 1
                    time.sleep(sleep_time)
                else:
                    logger.exception("Failed to Harvest ArXiV records for daterange: {}".format(self.daterange))
                    raise e

            self.parsed_records = iter(arxiv.ArxivParser.parse(self.raw_xml))

    def __next__(self):
        """
        Iterate through all parsed records. 
        If next(self.parsed_records) fails, we attempt to extract a resumptionToken and then rerun the harvest process with the token.
        
        return: 
            record: (str) XML of a single ArXiv record
        """
        try:
            record = next(self.parsed_records)
        except:
            try:
                resumptionToken = self.extract_resumptionToken(self.raw_xml)
            except:
                logger.debug("No resumptionToken present")
            if resumptionToken:
                self.harvest_arxiv(resumptionToken=resumptionToken)
                record = next(self.parsed_records)  
        
        yield record

    @staticmethod
    def extract_resumptionToken(raw_xml):
        """
        extracts the resumptionToken from the raw response. (ArXiv uses these for paging, see OAI harvesting docs for details).

        raw_xml: (str) XML content from ArXiv

        return: (str) ArXiv resumptionToken
        """
        arxiv_parser = arxiv.MultiArxivParser()
        token_text = arxiv_parser.get_chunks(raw_xml, r"<resumptionToken", r"</resumptionToken>")
        pattern = re.compile(r"[0-9]+\|[0-9]+")
        return pattern.search(token_text)[0]


