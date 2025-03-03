from abc import ABC, abstractmethod
from typing import List
import uuid
from domain.task.models import MultipleInvoicesTaskDataModel, SingleInvoiceTaskDataModel
from domain.task.schemas import (
    MultipleInvoicesAction,
    MultipleInvoicesIdentifier,
    MultipleInvoicesResponse,
    SingleInvoiceIdentifier,
    SingleInvoiceAction,
    SingleInvoiceResponse,
    SingleInvoiceStatusRequest,
    TaskStatus,
    TaskStatusResponse,
    TaskStatusUpdateByUUIDRequest,
    TaskType,
)


class TaskRepository(ABC):
    @abstractmethod
    def create_single_invoice_entry(
        self, action_type: SingleInvoiceAction, invoice: SingleInvoiceIdentifier
    ) -> SingleInvoiceTaskDataModel:
        pass

    @abstractmethod
    def create_multiple_invoice_entry(
        self, action_type: MultipleInvoicesAction, invoice: MultipleInvoicesIdentifier
    ) -> MultipleInvoicesTaskDataModel:
        pass

    @abstractmethod
    def get_single_invoice_tasks_status(
        self, tasks: List[SingleInvoiceIdentifier]
    ) -> List[TaskStatusResponse]:
        pass

    @abstractmethod
    def verify_company_task_ownership(
        self, company_uuid: uuid.UUID, tasks_uuid: List[uuid.UUID]
    ) -> bool:
        pass

    @abstractmethod
    def update_tasks_status(
        self,
        updated_tasks_data: List[TaskStatusUpdateByUUIDRequest],
    ) -> None:
        pass

    @abstractmethod
    def get_waiting_tasks_for_machine_single_invoice(
        self, company_uuid: uuid.UUID
    ) -> List[SingleInvoiceResponse]:
        pass

    @abstractmethod
    def get_waiting_tasks_for_machine_multiple_invoices(
        self, company_uuid: uuid.UUID
    ) -> List[MultipleInvoicesResponse]:
        pass

    @abstractmethod
    def single_invoice_entry_exists(self, idno: str, seria: str, number: int) -> bool:
        pass

    @abstractmethod
    def create_company_task(
        self,
        task_uuid: uuid.UUID,
        company_uuid: uuid.UUID,
        status: TaskStatus,
        task_type: TaskType,
    ):
        pass

    @abstractmethod
    def get_single_invoice_tasks_uuid(
        self, tasks: List[SingleInvoiceStatusRequest]
    ) -> List[uuid.UUID]:
        pass

