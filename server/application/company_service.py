from domain.company.company import Company
from domain.company.repository import CompanyRepository
from domain.exceptions import CompanyNotFoundException
from uuid import uuid4


class CompanyService:
    """Service layer for handling company-related business logic."""

    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def register_company(self, name: str) -> Company:
        """
        Register a new company with the given name.

        Args:
            name: Name of the company to register

        Returns:
            Company: Newly created company entity with generated UUID and auth token

        Raises:
            DatabaseException: If there's an error saving to the database
        """
        company = Company(name)
        self.company_repository.save(company)
        return company

    def regenerate_auth_token(self, current_token: str) -> Company:
        """
        Generate a new authentication token for a company.

        Args:
            current_token: Current authentication token of the company

        Returns:
            Company: Updated company entity with new auth token

        Raises:
            CompanyNotFoundException: If company with current token not found
            DatabaseException: If there's an error updating the database
        """
        # Get current token
        company = self.company_repository.find_by_token(current_token)
        if not company:
            raise CompanyNotFoundException("Company not found")

        # Generate new token
        new_token = str(uuid4())

        # Update company
        company.auth_token = new_token
        self.company_repository.update_company(company)

        return company
