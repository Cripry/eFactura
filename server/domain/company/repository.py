from abc import ABC, abstractmethod


class CompanyRepository(ABC):
    @abstractmethod
    def save(self, company):
        pass

    @abstractmethod
    def find_by_token(self, token: str):
        pass

    @abstractmethod
    def update(self, company):
        pass
