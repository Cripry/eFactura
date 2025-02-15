from enum import Enum
from selenium.webdriver.common.by import By


class LoginPageSelectors(Enum):
    LOGIN_INITIAL_BUTTON = (By.CLASS_NAME, "header-personal")
    LOGIN_MPASS_BUTTON = (By.CLASS_NAME, "mpass-card")
    LOGIN_MSIGN_BUTTON = (By.XPATH, "/html/body/main/div[2]/div[3]/a[2]")
    CERTIFICATES_CONTAINER = (By.XPATH, '//*[@id="certificates"]')
    PERSON_TYPE_SELECT = (
        By.XPATH,
        '//*[@id="app_vue"]/section/div/div/div/div/div[1]/div/select',
    )
    COMPANY_DROPDOWN = (
        By.XPATH,
        '//*[@id="app_vue"]/section/div/div/div/div/div[1]/div[2]/div',
    )
    COMPANIES_LIST = (
        By.XPATH,
        '//*[@id="app_vue"]/section/div/div/div/div/div[1]/div[2]/div/div',
    )
    COMPANY_ITEMS = (By.CLASS_NAME, "select-area-dropdown-item")
    ROLE_DROPDOWN = (
        By.XPATH,
        '//*[@id="app_vue"]/section/div/div/div/div/div[1]/div[3]/div/span',
    )
    ROLE_ITEMS = (By.CLASS_NAME, "role-item-blue")
    SET_BUTTON = (By.CSS_SELECTOR, "div.set_company-wrap a.btn-dark-blue")


class EFacturaSelectors(Enum):
    """Selectors for e-Factura website"""
    POPUP_CLOSE_BUTTON = (By.XPATH, '//*[@id="popupMessage"]/button')
