import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from domain.task.task import TaskStatus
from domain.company.models import CompanyModel

Base = declarative_base()


class TaskModel(Base):
    __tablename__ = "tasks"

    task_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idno = Column(String, nullable=False)
    seria = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("idno", "seria", "number", name="unique_task"),)


class CompanyTaskModel(Base):
    __tablename__ = "company_tasks"

    task_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey(TaskModel.task_uuid),
        nullable=False,
        primary_key=True,
    )
    company_uuid = Column(
        UUID(as_uuid=True), ForeignKey(CompanyModel.company_uuid), nullable=False
    )
    status = Column(String, nullable=False, default=TaskStatus.WAITING.value)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC)
    )
