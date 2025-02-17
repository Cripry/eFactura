from enum import Enum
from machine.invoice_signer_ddd.domain.services.efactura_web_page import EfacturaWebPage

class SupplierRoleSelectors(Enum):
    """Selectors specific to supplier role"""
    pass

class SupplierRoleEfactura(EfacturaWebPage):
    """Implementation of eFactura web page for supplier role"""
    def __init__(self, worker, web_handler):
        super().__init__(worker, web_handler)

    def navigate_to_section(self, section_name: str) -> bool:
        """Supplier-specific section navigation"""
        raise NotImplementedError

    def perform_action(self, action_name: str, *args) -> Optional[bool]:
        """Supplier-specific actions"""
        raise NotImplementedError 