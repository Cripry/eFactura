from enum import Enum


class UrlPaths(Enum):
    MOLDSIGN_LOGIN = "moldsign/login"
    EFACTURA = "efactura"


class QueryParams(Enum):
    AUTHENTIFICATION_TYPE = "authenticationType"


class CompanyUrls:
    URLS = {
        "TEST": "https://preproductie.sfs.md/ro/cabinetul-contribuabilului/companies-list",
        "PROD": "https://sfs.md/ro/cabinetul-contribuabilului/companies-list",
    }

    @classmethod
    def get_url(cls, environment: str) -> str:
        return cls.URLS.get(environment.upper())
