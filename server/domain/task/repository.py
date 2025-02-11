from abc import ABC, abstractmethod
from typing import List
from domain.task.task import Task, CompanyTask
import uuid


class TaskRepository(ABC):
    @abstractmethod
    def save_tasks(self, company_uuid: uuid.UUID, tasks: List[Task]) -> None:
        pass

    @abstractmethod
    def find_tasks_by_company(self, company_uuid: uuid.UUID) -> List[CompanyTask]:
        pass

    @abstractmethod
    def task_exists(self, idno: str, seria: str, number: int) -> bool:
        pass

    @abstractmethod
    def get_tasks_status(self, company_uuid: uuid.UUID, tasks: List[Task]) -> List[dict]:
        pass
