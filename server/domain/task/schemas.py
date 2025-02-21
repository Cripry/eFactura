import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from uuid import UUID
from pydantic import validator


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


class SingleInvoiceIdentifier(BaseModel):
    idno: str = Field(..., min_length=1, max_length=20)
    seria: Optional[str] = Field(None, min_length=1, max_length=10)
    number: int


class MultipleInvoicesIdentifier(BaseModel):
    idno: str = Field(..., min_length=1, max_length=20)


class SingleInvoiceTaskRequest(BaseModel):
    action_type: SingleInvoiceAction
    invoices: List[SingleInvoiceIdentifier]


class MultipleInvoicesTaskRequest(BaseModel):
    action_type: MultipleInvoicesAction
    invoices: List[MultipleInvoicesIdentifier]


class SingleInvoiceStatusRequest(BaseModel):
    idno: str
    seria: str
    number: str


class MultipleInvoicesStatusRequest(BaseModel):
    idno: str


class TaskStatusUpdateByUUIDRequest(BaseModel):
    task_uuid: UUID
    status: str

    @validator("status")
    def validate_status(cls, v):
        if v not in [status.value for status in TaskStatus]:
            raise ValueError("Invalid status")
        return v


class TaskStatusItem(BaseModel):
    idno: str
    seria: str
    number: str
    status: str


class TaskStatusResponse(BaseModel):
    tasks: List[TaskStatusItem]


class SingleInvoiceResponse(BaseModel):
    idno: str
    seria: str
    number: str
    task_uuid: str
    action_type: SingleInvoiceAction


class MultipleInvoicesResponse(BaseModel):
    idno: str
    task_uuid: str
    action_type: MultipleInvoicesAction


class CompanyTask(BaseModel):
    task_uuid: str
    company_uuid: str
    status: TaskStatus
    created_at: datetime.datetime
    task_type: TaskType
