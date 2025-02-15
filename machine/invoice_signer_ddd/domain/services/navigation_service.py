import time
from machine.invoice_signer_ddd.domain.models.urls import CompanyUrls
from machine.invoice_signer_ddd.domain.exceptions import NavigationException
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class NavigationService:
    def __init__(self, web_handler):
        self.web_handler = web_handler
        self.logger = logging.getLogger(__name__)

    def navigate_to_efactura(self, worker, driver):
        """Navigate to e-factura platform and select company"""
        try:
            # Use environment from web_handler
            self.logger.info("Navigating to companies list page")
            self.web_handler.navigate_to_url(
                CompanyUrls.get_url(self.web_handler.environment),
                retry_until_success=True,
            )

            # 2. Find all company rows
            self.logger.info("Looking for company grid items...")
            company_rows = self.web_handler.wait.wait_for_web_elements(
                (By.CLASS_NAME, "compania-grid-item--content")
            )

            if not company_rows:
                raise NavigationException("No company rows found on the page")

            # 3. Find company row by IDNO
            self.logger.info(f"Searching for company with IDNO: {worker.idno}")
            target_row = None

            for row in company_rows:
                try:
                    # Find span with company IDNO inside the row
                    idno_span = row.find_element(By.CLASS_NAME, "subtitle_name-company")
                    if worker.idno in idno_span.text:
                        self.logger.info(f"Found company row with IDNO {worker.idno}")
                        target_row = row
                        break
                except Exception:
                    continue

            if not target_row:
                raise NavigationException(
                    f"Company row with IDNO {worker.idno} not found"
                )

            # 4. Find and click Administration button
            self.logger.info("Clicking Administration button...")
            administration_button = target_row.find_element(
                By.CLASS_NAME, "btn_company-default"
            )
            administration_button.click()
            self.logger.info("Successfully clicked Administration button")

            # 5. Find and click e-Factura block
            self.logger.info("Looking for e-Factura block...")
            time.sleep(2)  # Wait for blocks to load

            services_blocks = self.web_handler.wait.wait_for_web_elements(
                (By.CLASS_NAME, "block_top-promoternus")
            )

            efactura_block = None
            for block in services_blocks:
                if "e-Factura" in block.text:
                    self.logger.info("Found e-Factura block")
                    efactura_block = block
                    break

            if not efactura_block:
                raise NavigationException("e-Factura block not found")

            # Store the current window handle before clicking
            original_window = driver.current_window_handle

            # Click e-Factura block which opens new window
            efactura_block.click()
            print("Clicked e-Factura block")
            time.sleep(2)  # Wait for new window

            # Wait for new window and switch to it
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

            # Switch to the new window
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            # Close original window
            driver.switch_to.window(original_window)
            driver.close()

            # Switch back to e-Factura window
            driver.switch_to.window(driver.window_handles[0])

            print("Successfully navigated to e-Factura")
            time.sleep(2)  # Wait for page to load

        except Exception as e:
            self.logger.error(f"Failed to navigate to e-factura platform: {str(e)}")
            raise NavigationException(str(e))
