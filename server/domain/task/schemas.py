from pydantic import BaseModel
from typing import List


class TaskRequest(BaseModel):
    IDNO: str
    seria: str
    number: int


class TaskStatusResponse(BaseModel):
    IDNO: str
    seria: str
    number: int
    status: str


class TaskStatusUpdateRequest(BaseModel):
    tasks: List[TaskRequest]
    status_update: str
