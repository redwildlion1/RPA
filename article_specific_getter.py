import selenium.common.exceptions as selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from date_formatter import DateFormatter
from datetime import datetime

class ArticleSpecificGetter:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def get_title(self, article, index):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".PagePromo-title"))
            )
            title = article.find_element(By.CSS_SELECTOR, ".PagePromo-title").text  # Adjust the selector
        except (selenium.NoSuchElementException):
            self.logger.warning("Title not found")
            title = ''
        except (selenium.StaleElementReferenceException):
            self.logger.warning("Stale element, trying to find the element again")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".PagePromo-title"))
            )
            article = self.driver.find_elements(By.CSS_SELECTOR, ".PageList-items-item")[index]
            title = article.find_element(By.CSS_SELECTOR, ".PagePromo-title").text

        return [article, title]

    def get_date(self, article):
        try:
            date_text = article.find_element(By.CSS_SELECTOR, ".Timestamp-template").text
        except (selenium.NoSuchElementException, selenium.StaleElementReferenceException):
            self.logger.info("Date not found")
            date_text = None
        if date_text:
            date = DateFormatter.process_date(date_text)
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        return date

    def get_description(self, article, index):
        try:
            description = article.find_element(By.CSS_SELECTOR, ".PagePromo-description").text  # Adjust the selector
        except selenium.NoSuchElementException:
            self.logger.info("Description not found")
            description = ''
        except selenium.ElementClickInterceptedException:
            decline_button_wrapper = self.driver.find_element(By.CSS_SELECTOR, ".lb-declinewrap")
            decline_button = decline_button_wrapper.find_element(By.CSS_SELECTOR, "a")
            decline_button.click()
            description = article.find_element(By.CSS_SELECTOR, ".PagePromo-description").text
        except selenium.StaleElementReferenceException:
            self.logger.warning("Stale element, trying to find the element again")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".PagePromo-description"))
            )
            article = self.driver.find_elements(By.CSS_SELECTOR, ".PageList-items-item")[index]
            description = article.find_element(By.CSS_SELECTOR, ".PagePromo-description").text

        return description

    def get_image_url(self, article):
        try:
            # Even though the image is not loaded, the URL is still present in the element
            # So we can get the URL without waiting for the image to load
            image_url = article.find_element(By.CSS_SELECTOR, ".Image").get_attribute("src")  # Adjust the selector
        except selenium.NoSuchElementException:
            self.logger.info("Image not found")
            image_url = None

        return image_url