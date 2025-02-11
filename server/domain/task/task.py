import uuid
import datetime
from enum import Enum
from dataclasses import dataclass


class TaskStatus(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    USB_NOT_FOUND = "usb_not_found"


@dataclass
class Task:
    task_uuid: uuid.UUID
    IDNO: str
    seria: str
    number: int


@dataclass
class CompanyTask:
    task_uuid: uuid.UUID
    company_uuid: uuid.UUID
    status: TaskStatus = TaskStatus.WAITING.value
    created_at: datetime.datetime = datetime.datetime.now(datetime.UTC)
