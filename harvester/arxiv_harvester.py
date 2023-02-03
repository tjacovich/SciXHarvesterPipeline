from OAIHarvester import OAIHarvester as OAI
import time
import logging as logger
import db
import xml_parsers
import re

MAX_RETRIES = 5
def arxiv_harvesting(app, job_request, config, producer):
    datestamp = job_request["task_args"].get("datestamp")
    resumptionToken = job_request["task_args"].get("resumptionToken")
    harvester = ArXiV_Harvester(config.get("ARXIV_OAI_URL"), daterange=datestamp, resumptionToken=resumptionToken)
    for record in harvester:
        arxiv_id = record.get("identifier")
        arxiv_dir, arxiv_name = harvester.arxiv_id_regex(arxiv_id)
        record_xml = record.get("xml")
        date = record.get("date")
        file_path = "/{}/{}".format(arxiv_dir, arxiv_name)

        etag = app.s3_methods.write_object_s3(file_bytes=bytes(record_xml), bucket=config.get('ARXIV_S3_BUCKET'), object_name=file_path)
        if etag:
            arxiv_id = "{}.{}".format(arxiv_dir, arxiv_name)
            existing_record = db.get_arxiv_record(arxiv_id)
            s3_key = file_path
            if not existing_record:
                produce = db.write_arxiv_record(app, arxiv_id, record_xml, date, s3_key, etag)

            elif existing_record.etag != etag:
                produce = db.update_arxiv_record(record_xml, date, etag)

            if produce:
                #placeholder code for producing to harvester output topic.
                producer.produce()
        else:
            return "Error"
    
    return "Success"

class ArXiV_Harvester(OAI):
    def __init__(self, harvest_url, daterange, resumptionToken):
        self.url = harvest_url
        self.params = {'metadataPrefix': 'oai_dc'}
        self.daterange = None
        self.parsed_records = self.harvest_arxiv(harvest_url, daterange, resumptionToken)

    @staticmethod
    def arxiv_id_regex(arxiv_id):
        """
        Simple regex for pulling the id from the arxix url.
        """
        pattern = re.compile(r"https://arxiv.org/abs/([0-9]{4}).([0-9]{5})")
        return pattern.match(arxiv_id).group(1), pattern.match(arxiv_id).group(2)

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
                raw_records = raw_response.json()
                success = True
            except  Exception as e:
                if raw_response.status_code == 503  and retries < MAX_RETRIES:
                    retries += 1 
                    sleep_time = 1
                    time.sleep(sleep_time)
                else:
                    logger.exception("Failed to Harvest ArXiV records for daterange: {}".format(daterange))
                    raise e

            self.parsed_records = xml_parsers.Split_ListRecords(raw_records)

    def __next__(self):
        record = next(self.parsed_records)

        if 'resumptionToken' in record.keys():
            self.harvest_arxiv(daterange=self.daterange, resumptionToken=record.get('resumptionToken'))
            record = next(self.parsed_records)
        
        yield record



