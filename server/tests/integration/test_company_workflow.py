from uuid import uuid4
import datetime


def test_company_auth_token_regeneration(db_session, company_service):
    # Arrange
    from domain.company.models import CompanyModel

    company = CompanyModel(
        company_uuid=uuid4(),
        name="Test Company",
        auth_token=str(uuid4()),
        created_at=datetime.datetime.now(),
    )
    db_session.add(company)
    db_session.flush()
    original_token = company.auth_token

    # Act
    new_token = company_service.regenerate_auth_token(company.company_uuid)

    # Refresh company from database
    db_session.refresh(company)

    # Assert
    assert new_token != original_token
    assert company.auth_token == new_token
