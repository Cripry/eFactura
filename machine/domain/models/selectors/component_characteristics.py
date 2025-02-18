from enum import Enum
from selenium.webdriver.common.by import By


class ComponentCharacteristics(Enum):
    CERTIFICATE_PAGE = (
        (By.XPATH, '//*[@id="select-certificate-view"]/h4'),
        {"text": "Selectați certificatul"},
    )
    SIGN_CONFIRMATION_POPUP = (
        (By.ID, "divHeaderMessage"),
        {"text": "Sunteți sigur(ă) că doriți să semnați elementele selectate?"},
    )
    MSIGN_SIGN_PAGE = (
        (By.XPATH, '//*[@id="stepperBox"]/div[1]/h4'),
        {"text": "Alegeți unul din instrumentele de semnare"},
    )
