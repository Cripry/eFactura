from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class TaskStatus(str, Enum):
    WAITING = "WAITING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    USB_NOT_FOUND = "USB_NOT_FOUND"


@dataclass
class Certificate:
    my_company_idno: str
    name: str
    status: str


@dataclass
class Task:
    seria: str
    number: int


@dataclass
class TaskResult:
    my_company_idno: str
    seria: str
    number: int
    status: TaskStatus
    error: Optional[str] = None


@dataclass
class CompanyTasks:
    my_company_idno: str
    tasks: List[Task]


@dataclass
class Session:
    my_company_idno: str
    person_name_certificate: str


@dataclass
class Worker:
    my_company_idno: str
    pin: str
    person_name_certificate: str
    role: str = "Administrator"
