from dataclasses import dataclass
from typing import List, Dict, Optional
from pydantic import BaseModel, RootModel
from enum import Enum


# Domain Models
class TaskStatus(str, Enum):
    WAITING = "WAITING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    USB_NOT_FOUND = "USB_NOT_FOUND"


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


class TaskRequest(BaseModel):
    idno: str
    seria: str
    number: int


# Request/Response Schemas
class MachineTasksResponse(RootModel):
    root: Dict[str, List[Dict[str, str]]]


class UpdateTaskStatusRequest(BaseModel):
    tasks: List[TaskRequest]
    status_update: TaskStatus
