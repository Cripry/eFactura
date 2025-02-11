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
            company_uuid=company.company_uuid,
            name=company.name,
            auth_token=company.auth_token,
            created_at=company.created_at,
        )
        self.session.add(company_model)
        self.session.commit()

    def find_by_token(self, token: str) -> Optional[Company]:
        company_model = (
            self.session.query(CompanyModel).filter_by(auth_token=token).first()
        )
        if company_model:
            return Company(
                name=company_model.name,
                auth_token=company_model.auth_token,
                company_uuid=company_model.company_uuid,
                created_at=company_model.created_at,
            )
        return None

    def update(self, company: Company):
        company_model = (
            self.session.query(CompanyModel)
            .filter_by(company_uuid=company.company_uuid)
            .first()
        )
        if company_model:
            company_model.auth_token = company.auth_token
            self.session.commit()
