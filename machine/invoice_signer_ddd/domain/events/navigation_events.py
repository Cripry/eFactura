from dataclasses import dataclass
from datetime import datetime


@dataclass
class NavigationStarted:
    destination: str
    timestamp: datetime = datetime.now()


@dataclass
class NavigationCompleted:
    destination: str
    timestamp: datetime = datetime.now()


@dataclass
class NavigationFailed:
    destination: str
    reason: str
    timestamp: datetime = datetime.now()
