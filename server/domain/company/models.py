import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class CompanyModel(Base):
    __tablename__ = "companies"

    company_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    auth_token = Column(String(255), nullable=False, unique=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
