from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from machine.invoice_signer_ddd.infrastructure.selenium.selectors import LoginPageSelectors


class LoginPage:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def get_username_field(self) -> WebElement:
        raise NotImplementedError

    def get_password_field(self) -> WebElement:
        raise NotImplementedError

    def get_login_button(self) -> WebElement:
        raise NotImplementedError

    def get_error_message(self) -> str:
        raise NotImplementedError

    def click_initial_button(self):
        element = self.driver.find_element(*LoginPageSelectors.INITIAL_BUTTON.value)
        element.click()

    def click_mpass_button(self):
        element = self.driver.find_element(*LoginPageSelectors.MPASS_BUTTON.value)
        element.click()

    def click_msign_button(self):
        element = self.driver.find_element(*LoginPageSelectors.MSIGN_BUTTON.value)
        element.click()

    def select_certificate(self, idno: str):
        container = self.driver.find_element(
            *LoginPageSelectors.CERTIFICATES_CONTAINER.value
        )
        certificates = container.find_elements_by_tag_name("div")

        for cert in certificates:
            if idno in cert.text:
                cert.click()
                return True
        return False
