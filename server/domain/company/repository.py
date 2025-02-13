from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from domain.company.company import Company


class CompanyRepository(ABC):
    @abstractmethod
    def save(self, company: Company) -> None:
        pass

    @abstractmethod
    def find_by_uuid(self, company_uuid: UUID) -> Optional[Company]:
        pass

    @abstractmethod
    def update_company(self, company: Company) -> None:
        pass
