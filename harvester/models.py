from sqlalchemy.ext.declarative import declarative_base
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum

Base = declarative_base()

class Status(enum.Enum):
    Pending = 1
    Processing = 2
    Error = 3
    Success = 4

class gRPC_status(Base):
    """
    gRPC table
    table containing the given status of every job passed through the gRPC API
    """
    __tablename__ = 'grpc_status'
    id = Column(Integer, primary_key=True)
    job_hash = Column(String, unique=True)
    job_request = Column(String)
    status = Column(Enum(Status))
    timestamp = Column(DateTime)

class ArXiV_record(Base):
    """
    ArXiV records table
    table containing the relevant information for harvested arxiv records.
    """
    __tablename__ = 'arxiv_records'
    id = Column(Integer)
    arxiv_id = Column(String, unique=True, primary_key=True)
    s3_key = Column(String)
    raw_xml = Column(String)
    date = Column(DateTime)
    etag = Column(String)
