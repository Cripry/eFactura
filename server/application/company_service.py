from domain.company.company import Company
from domain.company.repository import CompanyRepository


class CompanyService:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def register_company(self, name: str) -> Company:
        """Register a new company and return it with the generated token"""
        company = Company(name)
        self.company_repository.save(company)
        return company

    def regenerate_token(self, current_token: str) -> Company:
        """Regenerate token for an existing company"""
        company = self.company_repository.find_by_token(current_token)
        if not company:
            raise ValueError("Invalid token")

        company.regenerate_token()
        self.company_repository.update(company)
        return company
