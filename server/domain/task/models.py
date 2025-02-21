import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from domain.company.models import CompanyModel

Base = declarative_base()


class SingleInvoiceTaskDataModel(Base):
    __tablename__ = "single_invoice_task_data"

    task_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idno = Column(String(50), nullable=False)
    seria = Column(String(50), nullable=False)
    number = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)
    __table_args__ = (UniqueConstraint("idno", "seria", "number", name="unique_task"),)


class MultipleInvoicesTaskDataModel(Base):
    __tablename__ = "multiple_invoices_task_data"

    task_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idno = Column(String(50), nullable=False)
    action_type = Column(String(50), nullable=False)


class CompanyTaskModel(Base):
    __tablename__ = "company_tasks"

    task_uuid = Column(UUID(as_uuid=True), primary_key=True)
    company_uuid = Column(
        UUID(as_uuid=True), ForeignKey(CompanyModel.company_uuid), nullable=False
    )
    status = Column(String(50), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
    task_type = Column(String(50), nullable=False)
