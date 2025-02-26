from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from domain.company.company import Company
from application.company_service import CompanyService
from infrastructure.persistence.sqlalchemy_company_repository import (
    SQLAlchemyCompanyRepository,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from typing import List
from application.task_service import TaskService
from infrastructure.persistence.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from domain.exceptions import (
    DuplicateTaskException,
    TaskExistsException,
    InvalidStatusException,
    TaskNotOwnedException,
    DatabaseException,
    TaskNotFoundException,
)
from domain.task.schemas import (
    SingleInvoiceTaskRequest,
    MultipleInvoicesTaskRequest,
    SingleInvoiceStatusRequest,
    TaskStatusUpdateByUUIDRequest,
)

app = FastAPI()
security = HTTPBearer()

# Database setup
engine = create_engine(Config().SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models
class CompanyRegisterRequest(BaseModel):
    name: str


class TokenResponse(BaseModel):
    auth_token: str


# Authorization service
async def get_current_company(
    credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)
):
    auth_token = credentials.credentials
    repository = SQLAlchemyCompanyRepository(db)
    company = repository.find_by_token(auth_token)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return company


@app.post("/register", response_model=TokenResponse)
def register_company(request: CompanyRegisterRequest, db=Depends(get_db)):
    """
    Register a new company and generate its authentication token.

    Request Body:
    ```json
    {
        "name": "Company Name"
    }
    ```

    Returns:
    ```json
    {
        "auth_token": "generated-auth-token-string"
    }
    ```

    Notes:
        - The auth_token is unique for each company
        - Store this token securely as it will be needed for all future requests
        - Token is required in Authorization header for authenticated endpoints
    """
    repository = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repository)
    company = service.register_company(request.name)
    return {"auth_token": company.auth_token}


@app.post("/regenerate-token", response_model=TokenResponse)
def regenerate_auth_token(
    current_company: Company = Depends(get_current_company), db=Depends(get_db)
):
    """
    Generate a new authentication token for the company.

    Authentication:
        Requires current auth token in Authorization header
        Example: Authorization: Bearer <current_auth_token>

    Returns:
    ```json
    {
        "auth_token": "new-auth-token-string"
    }
    ```

    Notes:
        - Previous token becomes invalid immediately
        - Update your stored token with the new one
        - New token must be used for all subsequent requests
    """
    repository = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repository)
    company = service.regenerate_auth_token(current_company.auth_token)
    return {"auth_token": company.auth_token}


@app.post("/tasks/buyer/sign_single_invoice", status_code=status.HTTP_200_OK)
def create_single_invoice_task(
    request: SingleInvoiceTaskRequest,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    Create tasks for signing individual invoices as a buyer.

    Authentication:
        Requires Bearer token in Authorization header
        Example: Authorization: Bearer <auth_token>

    Request Body:
    ```json
    {
        "action_type": "BuyerSignInvoice",
        "invoices": [
            {
                "idno": "1234567890123",
                "person_name": "Person_Name",
                "seria": "AA",
                "number": 123
            }
        ]
    }
    ```

    Action Types:
        - BuyerSignInvoice: Sign invoice as a buyer
        (Future action types can be added here)

    Returns:
        200 OK: Tasks created successfully
        409 Conflict: Tasks already exist or duplicates found
        500 Internal Server Error: Database error

    Error Response Examples:
    ```json
    {
        "message": "Tasks already exist",
        "existing_tasks": [
            {
                "idno": "1234567890123",
                "person_name": "Person_Name",
                "seria": "AA",
                "number": 123
            }
        ]
    }
    ```
    """
    repository = SQLAlchemyTaskRepository(db)
    service = TaskService(repository)
    try:
        service.create_single_invoice_task(
            current_company, request.action_type, request.invoices
        )
        return JSONResponse(
            content={"message": "Single invoice tasks created successfully"},
            status_code=status.HTTP_200_OK,
        )
    except (DuplicateTaskException, TaskExistsException) as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": e.message,
                "duplicates": getattr(e, "duplicates", None),
                "existing_tasks": getattr(e, "existing_tasks", None),
            },
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@app.post("/tasks/supplier/sign_all_invoices", status_code=status.HTTP_200_OK)
def create_multiple_invoices_task(
    request: MultipleInvoicesTaskRequest,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    Create tasks for signing all invoices  from defined page in action_type as a supplier.

    Authentication:
        Requires Bearer token in Authorization header

    Request Body:
    ```json
    {
        "action_type": "SupplierSignAllDraftedInvoices",
        "invoices": [
            {
                "idno": "1234567890123",
                "person_name": "Person_Name"
            }
        ]
    }
    ```

    Action Types:
        - SupplierSignAllDraftedInvoices: Sign all drafted invoices for the company
        (Future action types can be added here)

    Returns:
        200 OK: Tasks created successfully
        409 Conflict: Duplicates found
        500 Internal Server Error: Database error
    """
    repository = SQLAlchemyTaskRepository(db)
    service = TaskService(repository)
    try:
        service.create_multiple_invoices_task(
            current_company, request.action_type, request.invoices
        )
        return JSONResponse(
            content={"message": "Multiple invoices task created successfully"},
            status_code=status.HTTP_200_OK,
        )
    except DuplicateTaskException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "code": e.code, "duplicates": e.duplicates},
        )

    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@app.post("/tasks/status/singleInvoice", status_code=status.HTTP_200_OK)
def get_single_invoice_tasks_status(
    tasks: List[SingleInvoiceStatusRequest],
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    Get status of single invoice tasks.

    Request Body:
    ```json
    [
        {
            "idno": "1234567890123",
            "seria": "AA",
            "number": "123"
        }
    ]
    ```

    Returns:
    ```json
    {
        "tasks": [
            {
                "idno": "1234567890123",
                "seria": "AA",
                "number": "123",
                "status": "WAITING"
            }
        ]
    }
    ```
    """
    task_repository = SQLAlchemyTaskRepository(db)
    task_service = TaskService(task_repository)

    try:
        result = task_service.get_single_invoice_tasks_status(current_company, tasks)
        return JSONResponse(content=result.dict(), status_code=status.HTTP_200_OK)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@app.put("/tasks/status")
def update_tasks_status(
    request: List[TaskStatusUpdateByUUIDRequest],
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    Update status of tasks by their UUIDs.

    Request Body:
    ```json
    [
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "status": "COMPLETED"
        }
    ]
    ```

    Task Statuses:
        - WAITING: Task is waiting to be processed
        - PROCESSING: Task is currently being processed
        - COMPLETED: Task has been completed successfully
        - FAILED: Task failed to complete
        - USB_NOT_FOUND: USB device required for signing was not found

    Returns:
        200 OK: Status updated successfully
        404 Not Found: Task not found
        403 Forbidden: Task doesn't belong to company
        400 Bad Request: Invalid status
        500 Internal Server Error: Database error
    """
    repository = SQLAlchemyTaskRepository(db)
    service = TaskService(repository)
    try:
        service.update_tasks_status_by_uuid(current_company, request)
        return JSONResponse(
            content={"message": "Tasks status updated successfully"},
            status_code=status.HTTP_200_OK,
        )
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": e.message,
                "code": e.code,
                "task_uuid": str(e.task_uuid),
            },
        )
    except InvalidStatusException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code},
        )
    except TaskNotOwnedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "code": e.code},
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@app.get("/machine/tasks", status_code=status.HTTP_200_OK)
def get_structured_waiting_tasks_for_machine(
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """
    Get all waiting tasks structured by person name and IDNO for the machine.

    Returns:
    ```json
    {
        "SingleInvoiceTask": {
            "Person_Name": {
                "IDNO1": [
                    {
                        "seria": "AA",
                        "number": "123",
                        "task_uuid": "uuid",
                        "action_type": "BuyerSignInvoice"
                    }
                ]
            }
        },
        "MultipleInvoicesTask": [
            {
                "idno": "IDNO1",
                "task_uuid": "uuid",
                "action_type": "SupplierSignAllDraftedInvoices"
            }
        ]
    }
    ```
    """
    try:
        task_repository = SQLAlchemyTaskRepository(db)
        task_service = TaskService(task_repository)
        result = task_service.get_structured_waiting_tasks_for_machine(current_company)
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@app.exception_handler(DuplicateTaskException)
async def duplicate_task_exception_handler(request, exc: DuplicateTaskException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "message": exc.message,
            "code": exc.code,
            "duplicates": exc.duplicates,
        },
    )


@app.exception_handler(TaskExistsException)
async def task_exists_exception_handler(request, exc: TaskExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "message": exc.message,
            "code": exc.code,
            "existing_tasks": exc.existing_tasks,
        },
    )


@app.exception_handler(InvalidStatusException)
async def invalid_status_exception_handler(request, exc: InvalidStatusException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message, "code": exc.code},
    )


@app.exception_handler(TaskNotOwnedException)
async def task_not_owned_exception_handler(request, exc: TaskNotOwnedException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": exc.message, "code": exc.code, "task": exc.task_details},
    )


@app.exception_handler(DatabaseException)
async def database_exception_handler(request, exc: DatabaseException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": exc.message, "code": exc.code, "details": exc.details},
    )


@app.exception_handler(TaskNotFoundException)
async def task_not_found_exception_handler(request, exc: TaskNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": exc.message,
            "code": exc.code,
            "task_uuid": str(exc.task_uuid),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7989)
