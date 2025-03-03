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
    idno: str
    name: str
    status: str


@dataclass
class Task:
    seria: str
    number: int


@dataclass
class TaskResult:
    idno: str
    seria: str
    number: int
    status: TaskStatus
    error: Optional[str] = None


@dataclass
class CompanyTasks:
    idno: str
    tasks: List[Task]


@dataclass
class Session:
    idno: str
    person_name: str

@dataclass
class Worker:
    idno: str
    pin: str
    person_name: str
    role: str = "Administrator"
