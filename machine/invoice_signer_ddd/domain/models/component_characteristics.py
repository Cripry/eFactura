from enum import Enum
from selenium.webdriver.common.by import By


class ComponentCharacteristics(Enum):
    CERTIFICATE_PAGE = (
        (By.XPATH, '//*[@id="select-certificate-view"]/h4'),
        {"text": "Selectați certificatul"},
    )
