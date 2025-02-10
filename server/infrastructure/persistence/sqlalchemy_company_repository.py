from sqlalchemy.orm import Session
from domain.company.repository import CompanyRepository
from domain.company.company import Company
from domain.company.models import CompanyModel
from typing import Optional


class SQLAlchemyCompanyRepository(CompanyRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, company: Company):
        company_model = CompanyModel(
            id=company.id,
            name=company.name,
            auth_token=company.auth_token,
            created_at=company.created_at
        )
        self.session.add(company_model)
        self.session.commit()

    def find_by_token(self, token: str) -> Optional[Company]:
        company_model = self.session.query(CompanyModel).filter_by(auth_token=token).first()
        if company_model:
            return Company(
                name=company_model.name,
                auth_token=company_model.auth_token,
                id=company_model.id,
                created_at=company_model.created_at
            )
        return None

    def update(self, company: Company):
        company_model = self.session.query(CompanyModel).filter_by(id=company.id).first()
        if company_model:
            company_model.auth_token = company.auth_token
            self.session.commit()
