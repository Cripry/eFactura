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
from uuid import UUID

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


class TaskRequest(BaseModel):
    IDNO: str
    seria: str
    number: int


class TaskStatusResponse(BaseModel):
    IDNO: str
    seria: str
    number: int
    status: str


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
def regenerate_token(
    current_company: Company = Depends(get_current_company), db=Depends(get_db)
):
    repository = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repository)
    company = service.regenerate_token(current_company.auth_token)
    return {"auth_token": company.auth_token}


@app.post("/tasks", status_code=status.HTTP_200_OK)
def create_tasks(
    tasks: List[TaskRequest],
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    task_repository = SQLAlchemyTaskRepository(db)
    task_service = TaskService(task_repository)

    print("current_company.company_uuid: ", current_company.company_uuid)
    result = task_service.create_tasks(current_company.company_uuid, tasks)

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7989)
