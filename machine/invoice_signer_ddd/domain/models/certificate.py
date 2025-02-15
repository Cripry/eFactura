from dataclasses import dataclass


@dataclass
class Certificate:
    idno: str
    name: str
    status: str
