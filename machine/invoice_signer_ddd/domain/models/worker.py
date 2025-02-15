from dataclasses import dataclass


@dataclass
class Worker:
    idno: str
    pin: str
    role: str = "Administrator"
