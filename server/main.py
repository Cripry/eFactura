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
)
from domain.task.schemas import TaskRequest, TaskStatusUpdateRequest

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
    repository = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repository)
    company = service.register_company(request.name)
    return {"auth_token": company.auth_token}


@app.post("/regenerate-token", response_model=TokenResponse)
def regenerate_auth_token(
    current_company: Company = Depends(get_current_company), db=Depends(get_db)
):
    repository = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repository)
    company = service.regenerate_auth_token(current_company.auth_token)
    return {"auth_token": company.auth_token}


@app.post("/tasks", status_code=status.HTTP_200_OK)
def create_tasks(
    tasks: List[TaskRequest],
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    repository = SQLAlchemyTaskRepository(db)
    service = TaskService(repository)
    try:
        return service.create_tasks(current_company.company_uuid, tasks)
    except (DuplicateTaskException, TaskExistsException) as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": e.message,
                "code": e.code,
                "duplicates": getattr(e, "duplicates", None),
                "existing_tasks": getattr(e, "existing_tasks", None),
            },
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@app.post("/tasks/status", status_code=status.HTTP_200_OK)
def get_tasks_status(
    tasks: List[TaskRequest],
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    task_repository = SQLAlchemyTaskRepository(db)
    task_service = TaskService(task_repository)

    result = task_service.get_tasks_status(current_company.company_uuid, tasks)
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@app.get("/machine/tasks", status_code=status.HTTP_200_OK)
def get_machine_tasks(
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    task_repository = SQLAlchemyTaskRepository(db)
    task_service = TaskService(task_repository)

    result = task_service.get_waiting_tasks_for_machine(current_company.company_uuid)
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@app.put("/tasks/status", status_code=status.HTTP_200_OK)
def update_tasks_status(
    request: TaskStatusUpdateRequest,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    repository = SQLAlchemyTaskRepository(db)
    service = TaskService(repository)
    try:
        return service.update_tasks_status(
            current_company.company_uuid, request.tasks, request.status_update
        )
    except InvalidStatusException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code},
        )
    except TaskNotOwnedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": e.message, "code": e.code, "task": e.task_details},
        )
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7989)
