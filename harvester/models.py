from sqlalchemy.types import TypeDecorator
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
    User table
    Foreign-key absolute_uid is the primary key of the user in the user
    database microservice.
    """
    __tablename__ = 'grpc_status'
    id = Column(Integer, primary_key=True)
    job_hash = Column(String, unique=True)
    job_request = Column(String)
    status = Column(Enum(Status))
    timestamp = Column(DateTime)
