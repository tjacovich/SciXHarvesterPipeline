from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()

# class HexByteString(TypeDecorator):
#     """Convert Python bytestring to string with hexadecimal digits and back for storage."""

#     impl = String

#     def process_bind_param(self, value, dialect):
#         if not isinstance(value, bytes):
#             raise TypeError("HexByteString columns support only bytes values.")
#         return value.hex()

#     def process_result_value(self, value, dialect):
#         return bytes.fromhex(value) if value else None

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
    status = Column(String)
    timestamp = Column(DateTime)
