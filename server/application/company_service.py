from domain.company.company import Company
from domain.company.repository import CompanyRepository
from domain.exceptions import CompanyNotFoundException
import uuid
from uuid import uuid4


class CompanyService:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def register_company(self, name: str) -> Company:
        """Register a new company and return it with the generated token"""
        company = Company(name)
        self.company_repository.save(company)
        return company

    def regenerate_auth_token(self, company_uuid: uuid.UUID) -> str:
        """Regenerate token for an existing company"""
        # Get current token
        company = self.company_repository.find_by_uuid(company_uuid)
        if not company:
            raise CompanyNotFoundException("Company not found")

        # Generate new token
        new_token = str(uuid4())

        # Update company
        company.auth_token = new_token
        self.company_repository.update_company(company)

        return new_token
