#LOGGING_LEVEL = 'WARN'
#LOGGING_LEVEL = 'DEBUG'
LOGGING_LEVEL = 'INFO'
LOG_STDOUT = True
#SQLALCHEMY Configuration
SQLALCHEMY_URL = 'postgres://grpc_status:gRPC_status@postgres:5432/grpc_status'
SQLALCHEMY_ECHO = False
#REDIS Configuration
REDIS_HOST = 'redis'
REDIS_PORT = 6379
#Kafka Configuration
KAFKA_BROKER = 'kafka:9092'
SCHEMA_REGISTRY_URL = 'http://schema-registry:8081'
#Harvester AVRO schema ID
SCHEMA_ID = '1'
#AWS Configuration
AWS_ACCESS_KEY_ID = 'CHANGEME'
AWS_SECRET_ACCESS_KEY = 'SECRETS'
AWS_DEFAULT_REGION = 'us-east-1'
PROFILE_NAME = 'SESSION_PROFILE'
#OAI Harvesting urls
ARXIV_OAI_URL='https://export.arxiv.org/oai2'