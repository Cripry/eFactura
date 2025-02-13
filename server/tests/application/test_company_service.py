import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from application.company_service import CompanyService
from domain.company.models import CompanyModel
import datetime


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def company_service(mock_repository):
    return CompanyService(mock_repository)


@pytest.fixture
def test_company():
    return CompanyModel(
        company_uuid=uuid4(),
        name="Test Company",
        auth_token=str(uuid4()),
        created_at=datetime.datetime.now(),
    )


def test_regenerate_auth_token(company_service, mock_repository, test_company):
    # Arrange
    original_token = test_company.auth_token

    # Mock repository responses
    mock_repository.get_company_by_uuid.return_value = test_company
    mock_repository.update_company.return_value = None

    # Act
    new_token = company_service.regenerate_auth_token(test_company.company_uuid)

    # Assert
    assert new_token != original_token
