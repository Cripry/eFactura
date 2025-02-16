from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserAuthenticated:
    user_id: str
    timestamp: datetime = datetime.now()


@dataclass
class AuthenticationFailed:
    user_id: str
    reason: str
    timestamp: datetime = datetime.now()
