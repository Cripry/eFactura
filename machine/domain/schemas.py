from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List
from uuid import UUID


class SingleInvoiceAction(str, Enum):
    BUYER_SIGN_INVOICE = "BuyerSignInvoice"
    # Add other single invoice actions as needed


class MultipleInvoicesAction(str, Enum):
    SUPPLIER_SIGN_ALL_DRAFTED_INVOICES = "SupplierSignAllDraftedInvoices"
    # Add other multiple invoices actions as needed


class TaskType(str, Enum):
    SINGLE_INVOICE_TASK = "SingleInvoiceTask"
    MULTIPLE_INVOICES_TASK = "MultipleInvoicesTask"


class TaskStatus(str, Enum):
    WAITING = "WAITING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    USB_NOT_FOUND = "USB_NOT_FOUND"


class SignatureType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SingleInvoiceTask(BaseModel):
    seria: str
    number: str
    task_uuid: str
    action_type: SingleInvoiceAction


class MultipleInvoicesTask(BaseModel):
    my_company_idno: str
    buyer_idno: str
    signature_type: SignatureType
    task_uuid: str
    action_type: MultipleInvoicesAction


class MachineTasksResponse(BaseModel):
    model_config = ConfigDict(extra="allow")  # Allow dynamic field names

    def __init__(self, **data):
        # Transform the data to use TaskType enum values as keys
        transformed_data = {
            TaskType.SINGLE_INVOICE_TASK.value: data.get(
                TaskType.SINGLE_INVOICE_TASK.value, {}
            ),
            TaskType.MULTIPLE_INVOICES_TASK.value: data.get(
                TaskType.MULTIPLE_INVOICES_TASK.value, []
            ),
        }
        super().__init__(**transformed_data)


class TaskStatusUpdate(BaseModel):
    task_uuid: UUID
    status: TaskStatus

    @classmethod
    def create(cls, task_uuid: str, status: TaskStatus) -> "TaskStatusUpdate":
        return cls(task_uuid=task_uuid, status=status)


class TaskStatusUpdateRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    tasks: List[TaskStatusUpdate]
