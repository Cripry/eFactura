from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By


class WebDriverFacade:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def find_element(self, by: By, value: str):
        return self.driver.find_element(by, value)

    def find_elements(self, by: By, value: str):
        return self.driver.find_elements(by, value)

    def get(self, url: str):
        self.driver.get(url)

    def current_url(self) -> str:
        return self.driver.current_url
