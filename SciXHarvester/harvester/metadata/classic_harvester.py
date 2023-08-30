import json
import uuid
from datetime import datetime

from SciXPipelineUtils import utils

from harvester import db


def classic_harvesting(app, job_request, producer):
    """
    Main harvesting routine for record from the Legacy backoffice system.

    job_request: (json) task message passed to Harvester input topic.
    producer: The harvester kafka producer instance

    return: (str) The final state of the harvesting process.
    """
    datestamp = datetime.now().strftime("%Y%m%d")
    harvester_output_schema = utils.get_schema(
        app, app.schema_client, app.config.get("HARVESTER_OUTPUT_SCHEMA")
    )

    db_record = job_request.get("after")
    # Assign ID to new record
    record_id = uuid.uuid4()
    # Generate filepath for S3
    file_path = "/MASTER_DB/{}/{}".format(datestamp, record_id)
    record = json.dumps(db_record.get("HARVESTER_CLASSIC_TOPIC.Value"))
    # write record to S3
    checksum = None
    for provider in app.s3Clients.keys():
        try:
            checksum = app.s3Clients[provider].write_object_s3(
                file_bytes=bytes(record, "utf-8"), object_name=file_path
            )
        except Exception as e:
            app.logger.error(
                "Failed to write to S3 provider: {} with Exception: {}".format(provider, e)
            )

    if checksum:
        app.logger.debug("AWS checksum for {} is: {}".format(record_id, checksum))
        s3_key = file_path
        produce = db.write_harvester_record(
            app, record_id, datetime.now(), s3_key, checksum, job_request.get("task")
        )
        if produce:
            producer_message = {
                "record_id": str(record_id),
                "record_xml": record,
                "s3_path": file_path,
                "task": job_request.get("task"),
                "datetime": datetime.now(),
            }
            producer.produce(
                topic=app.config.get("HARVESTER_OUTPUT_TOPIC"),
                value=producer_message,
                value_schema=harvester_output_schema,
            )
    else:
        app.logger.error("No checksums generated, S3 upload must have failed. Stopping.")
        return "Error"

    return "Success"
