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
def regenerate_token(
    current_company: Company = Depends(get_current_company), db=Depends(get_db)
):
    repository = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repository)
    company = service.regenerate_token(current_company.auth_token)
    return {"auth_token": company.auth_token}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7989)
