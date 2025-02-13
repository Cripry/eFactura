import uuid
import hashlib
import time
import datetime
from typing import Optional


class Company:
    def __init__(
        self,
        name: str,
        auth_token: Optional[str] = None,
        company_uuid: Optional[uuid.UUID] = None,
        created_at: Optional[datetime.datetime] = None,
    ):
        self.company_uuid = company_uuid or uuid.uuid4()
        self.name = name
        self.auth_token = auth_token or self._generate_token()
        self.created_at = created_at or datetime.datetime.now(datetime.UTC)

    def _generate_token(self) -> str:
        """Generate a unique auth token for the company"""
        raw_token = f"{self.name}{time.time()}{uuid.uuid4()}"
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def regenerate_auth_token(self) -> str:
        """Regenerate the auth token"""
        self.auth_token = self._generate_token()
        return self.auth_token
