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
    SELECT_AREA_DROPDOWN = (By.CLASS_NAME, "select-area-dropdown")

    ROLE_DROPDOWN = (
        By.XPATH,
        '//*[@id="app_vue"]/section/div/div/div/div/div[1]/div[3]/div/span',
    )
    ROLE_ITEMS = (By.CLASS_NAME, "role-item-blue")
    SET_BUTTON = (By.CSS_SELECTOR, "div.set_company-wrap a.btn-dark-blue")


class EFacturaSelectors(Enum):
    """Selectors for e-Factura website"""

    POPUP_CLOSE_BUTTON = (By.XPATH, '//*[@id="popupMessage"]/button')
    SERIA_INPUT = (
        By.XPATH,
        '//*[@id="sec_info"]/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/input[2]',
    )
    NUMBER_INPUT = (
        By.XPATH,
        '//*[@id="sec_info"]/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/input[2]',
    )
    SEARCH_BUTTON = (By.XPATH, '//*[@id="content"]/div[3]/div/div[1]/div[2]/a[2]')
    INVOICE_TABLE = (
        By.XPATH,
        '//*[@id="content"]/div[3]/div/div[3]/div[1]/table/tbody',
    )
    START_SIGN_BUTTON = (By.XPATH, '//*[@id="content"]/div[3]/div/div[2]/div[1]/a[3]')
    FINAL_SIGN_BUTTON = (By.XPATH, '//*[@id="btnSign"]')
    SELECT_ALL_CHECKBOX = (
        By.XPATH,
        '//*[@id="content"]/div[3]/div/div[3]/table/tbody/tr/td[1]/input',
    )

    BUYER_INPUT_FIELD = (
        By.XPATH,
        '//*[@id="sec_info"]/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td/div',
    )

    BUYER_FIRST_INPUT_CHOISE = (By.CSS_SELECTOR, ".fm-popup a.fm-o-a:first-of-type")
    FIND_COMPANY_BUTTON = (By.XPATH, '//*[@id="content"]/div[3]/div/div[1]/div[2]/a[2]')

    SHORT_RADIO_BUTTON = (By.XPATH, '//*[@id="sendtoBuyer-confirmcircle"]/div/input[1]')
    LONG_RADIO_BUTTON = (By.XPATH, '//*[@id="sendtoBuyer-confirmcircle"]/div/input[2]')


class SFSSelectors(Enum):
    """Selectors for SFS portal"""

    COMPANY_GRID_ITEM = (By.CLASS_NAME, "compania-grid-item--content")
    COMPANY_my_company_idno = (By.CLASS_NAME, "subtitle_name-company")
    ADMIN_BUTTON = (By.CLASS_NAME, "btn_company-default")
    EFACTURA_BLOCK = (By.CLASS_NAME, "inner_block_top-promoternus")


class MSignSelectors(Enum):
    """Selectors for MSign website"""

    USB_SIGN_OPTION = (By.CLASS_NAME, "authentification-block")
    CERTIFICATE_CARDS = (By.CLASS_NAME, "card")
    SIGN_BUTTON = (By.CLASS_NAME, "btn")
