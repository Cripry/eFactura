from abc import ABC, abstractmethod
from typing import List
from domain.task.task import Task, CompanyTask
import uuid
from domain.task.schemas import TaskStatusUpdateRequest


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
    def get_tasks_status(
        self, company_uuid: uuid.UUID, tasks: List[Task]
    ) -> List[dict]:
        pass

    @abstractmethod
    def get_waiting_tasks_by_company(self, company_uuid: uuid.UUID) -> List[Task]:
        pass

    @abstractmethod
    def update_tasks_status(
        self, company_uuid: uuid.UUID, tasks: List[Task], task_data: List[TaskStatusUpdateRequest]
    ) -> int:
        pass

    @abstractmethod
    def task_belongs_to_company(
        self, company_uuid: uuid.UUID, idno: str, seria: str, number: int
    ) -> bool:
        pass
