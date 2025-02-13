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
    IDNO: str
    seria: str
    number: int
    status_update: str
