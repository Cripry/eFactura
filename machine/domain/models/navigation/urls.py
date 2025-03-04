from enum import Enum


class UrlPaths(Enum):
    MOLDSIGN_LOGIN = "moldsign/login"
    EFACTURA = "efactura"


class QueryParams(Enum):
    AUTHENTIFICATION_TYPE = "authenticationType"


class CompanyUrls:
    """URLs for company selection page"""

    URLS = {
        "TEST": "https://preproductie.sfs.md/ro/cabinetul-contribuabilului/companies-list",
        "PROD": "https://sfs.md/ro/cabinetul-contribuabilului/companies-list",
    }

    @classmethod
    def get_url(cls, environment: str) -> str:
        """Get URL for specified environment"""
        return cls.URLS.get(environment.upper())


class EfacturaBaseUrls:
    URLS = {
        "TEST": "https://efactura-pre.sfs.md",
        "PROD": "https://efactura.sfs.md",
    }

    @classmethod
    def get_base_url(cls, environment: str) -> str:
        return cls.URLS.get(environment.upper())


class SFSBaseUrls:
    SFS_BASE_URLS = {
        "TEST": "https://preproductie.sfs.md/ro",
        "PROD": "https://sfs.md/ro",
    }

    @classmethod
    def get_base_url(cls, environment: str) -> str:
        return cls.SFS_BASE_URLS.get(environment.upper())


class EfacturaUrls(Enum):
    """Common URLs for eFactura"""

    pass


class BuyerUrls(Enum):
    """URLs specific to buyer role"""

    INVOICES_TO_SIGN = "/#Home/ToAccept"


class SupplierUrls(Enum):
    """URLs specific to supplier role"""

    NEW_INVOICE = "/#Home/My_Draft"
    APPLYIED_FIRST_SIGNATURE = "/#Home/Signed_1"
