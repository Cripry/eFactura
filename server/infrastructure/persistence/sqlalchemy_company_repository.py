from domain.company.repository import CompanyRepository
from domain.company.company import Company
from domain.company.models import CompanyModel
from typing import Optional
import uuid


class SQLAlchemyCompanyRepository(CompanyRepository):
    """Repository implementation for company-related database operations using SQLAlchemy."""

    def __init__(self, session):
        self.session = session

    def save(self, company: Company) -> Company:
        """
        Save a new company to the database.

        Args:
            company: Company entity to save

        Returns:
            Company: Saved company entity with any auto-generated fields

        Raises:
            DatabaseException: If there's an error saving to the database
        """
        company_model = CompanyModel(
            company_uuid=company.company_uuid,
            name=company.name,
            auth_token=company.auth_token,
            created_at=company.created_at,
        )
        self.session.add(company_model)
        self.session.commit()
        return company

    def find_by_token(self, auth_token: str) -> Optional[Company]:
        """
        Find a company by its authentication token.

        Args:
            auth_token: Authentication token to search for

        Returns:
            Optional[Company]: Company if found, None otherwise

        Raises:
            DatabaseException: If there's an error querying the database
        """
        company_model = (
            self.session.query(CompanyModel).filter_by(auth_token=auth_token).first()
        )
        if company_model:
            return Company(
                name=company_model.name,
                auth_token=company_model.auth_token,
                company_uuid=company_model.company_uuid,
                created_at=company_model.created_at,
            )
        return None

    def find_by_uuid(self, company_uuid: uuid.UUID) -> Optional[Company]:
        company_model = (
            self.session.query(CompanyModel)
            .filter_by(company_uuid=company_uuid)
            .first()
        )
        if company_model:
            return Company(
                name=company_model.name,
                auth_token=company_model.auth_token,
                company_uuid=company_model.company_uuid,
                created_at=company_model.created_at,
            )
        return None

    def update_company(self, company: Company) -> None:
        company_model = (
            self.session.query(CompanyModel)
            .filter_by(company_uuid=company.company_uuid)
            .first()
        )
        if company_model:
            company_model.name = company.name
            company_model.auth_token = company.auth_token
            self.session.commit()

    def update_auth_token(self, current_token: str, new_token: str) -> Company:
        """
        Update a company's authentication token.

        Args:
            current_token: Current authentication token
            new_token: New authentication token to set

        Returns:
            Company: Updated company entity

        Raises:
            CompanyNotFoundException: If company with current token not found
            DatabaseException: If there's an error updating the database
        """
        company_model = (
            self.session.query(CompanyModel)
            .filter_by(auth_token=current_token)
            .first()
        )
        if company_model:
            company_model.auth_token = new_token
            self.session.commit()
            return Company(
                name=company_model.name,
                auth_token=company_model.auth_token,
                company_uuid=company_model.company_uuid,
                created_at=company_model.created_at,
            )
        raise CompanyNotFoundException("Company not found")
