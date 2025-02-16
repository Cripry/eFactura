from dataclasses import dataclass


@dataclass
class Session:
    idno: str
    token: str = None
    expiration: int = None
