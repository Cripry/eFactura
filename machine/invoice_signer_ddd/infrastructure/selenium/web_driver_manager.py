from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class WebDriverManager:
    def get_driver(self) -> webdriver.Chrome:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def close_driver(self, driver: webdriver.Chrome) -> None:
        driver.quit()