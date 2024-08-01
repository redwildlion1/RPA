from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common import exceptions as selenium
from logger import SimpleLogger
from article_specific_getter import ArticleSpecificGetter

class NewsDataExtractor:
    def __init__(self, driver, search_phrase, news_category, num_months, _logger):
        self.driver = driver
        self.search_phrase = search_phrase
        self.news_category = news_category
        self.num_months = num_months
        self.logger = _logger
        self.article_getter = ArticleSpecificGetter(self.driver, self.logger)

    def get_to_article_page(self):
        try:
            self.driver.get("https://apnews.com")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#onetrust-reject-all-handler")))
            reject_button = self.driver.find_element(By.CSS_SELECTOR, "#onetrust-reject-all-handler")  
            reject_button.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".SearchOverlay-search-button")))
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".SearchOverlay-search-button")))
            search_icon = self.driver.find_element(By.CSS_SELECTOR, ".SearchOverlay-search-button")  
            search_icon.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "q"))
            )
            search_box = self.driver.find_element(By.NAME, "q")  
            search_box.send_keys(self.search_phrase)
            search_box.submit()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".SearchResultsModule-wrapper"))  
            )
        except selenium.ElementNotInteractableException:
            self.logger.error("Element not interactable, getting to the article page failed")
        except selenium.TimeoutException:
            self.logger.error("Timeout while waiting for element")
            raise
             

    def select_category(self):
        categories = self.driver.find_elements(By.CSS_SELECTOR, ".SearchFilter-items-item")
        for category in categories:
            self.logger.info("Checking category: " + category.find_element(By.CSS_SELECTOR, "span").text)
            # Check if the category is the one we are looking for , it's in a span tag
            if category.find_element(By.CSS_SELECTOR, "span").text == self.news_category:
                input_category = category.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']"))
                    )
                except Exception as e:
                    self.logger.error("An error occurred while waiting for the checkbox to be clickable: " + str(e))
                    raise
                try:
                    input_category.click()
                except Exception as e:
                    self.logger.error("An error occurred while selecting the category: " + str(e))
                    raise
                self.logger.info("Category selected")
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".SearchResultsModule-wrapper"))
                )
                break


    def sort_by_newest(self) :
        self.driver.get(self.driver.current_url + "&s=3")
        # Wait for the page to change
        try:
            WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "option[value='3'][selected='']"))
            )
        except selenium.TimeoutException:
            # If the page doesn't change, reload the page with the parameters // This is a workaround
            self.logger.warning("Page didn't load properly, reloading the page")
            self.driver.get("https://apnews.com/search?q=" + self.search_phrase + "&s=3")
        except selenium.ElementClickInterceptedException:
            decline_button_wrapper = self.driver.find_element(By.CSS_SELECTOR, ".lb-declinewrap")
            decline_button = decline_button_wrapper.find_element(By.CSS_SELECTOR, "a")
            decline_button.click()
            self.driver.get("https://apnews.com/search?q=" + self.search_phrase + "&s=3")
        except selenium.ElementNotInteractableException:
            self.logger.error("Element not interactable, sorting by newest failed")
            raise

    def navigate_to_next_page(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".Pagination-nextPage"))
            )
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, ".Pagination-nextPage")
        except selenium.NoSuchElementException:
            # If the next page button is not found, it means we are on the last page
            return False
        except selenium.ElementClickInterceptedException:
            decline_button_wrapper = self.driver.find_element(By.CSS_SELECTOR, ".lb-declinewrap")
            decline_button = decline_button_wrapper.find_element(By.CSS_SELECTOR, "a")
            decline_button.click()
            raise selenium.ElementClickInterceptedException
        except selenium.ElementNotInteractableException:
            self.logger.error("Element not interactable, navigating to the next page failed")
            raise selenium.ElementNotInteractableException
        except selenium.StaleElementReferenceException:
            self.logger.warning("Stale element, trying to find the element again")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".Pagination-nextPage"))
            )
        next_page_button = self.driver.find_element(By.CSS_SELECTOR, ".Pagination-nextPage")
        next_page_button.click()
        self.logger.info("Navigating to the next page")
        return True
       

    def get_articles_from_wrapper(self):
        try:
            WebDriverWait(self.driver, 10).until(
                # CSS Selector bugs out, using XPATH
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/bsp-search-results-module/form/div[2]/div/bsp-search-filters/div/main/div[2]"))
            )
            results = self.driver.find_element(By.XPATH, "/html/body/div[3]/bsp-search-results-module/form/div[2]/div/bsp-search-filters/div/main/div[2]")
            articles_wrapper = results.find_element(By.CSS_SELECTOR, ".PageList-items")  
            self.driver.execute_script("arguments[0].scrollIntoView(true);", articles_wrapper)
            self.logger.info("Getting articles from the wrapper")
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".PageList-items-item"))
            )
            articles = articles_wrapper.find_elements(By.CSS_SELECTOR, ".PageList-items-item") 
            return articles
        except selenium.StaleElementReferenceException:
            self.logger.warning("Stale element, trying to find the element again")
            WebDriverWait(self.driver, 10).until(
                EC.element_located_to_be_selected((By.CSS_SELECTOR, ".SearchResultsModule-results"))
            )
            results = self.driver.find_element(By.CSS_SELECTOR, ".SearchResultsModule-results")
            articles_wrapper = results.find_element(By.CSS_SELECTOR, ".PageList-items")  
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".PageList-items-item"))
            )
            articles = articles_wrapper.find_elements(By.CSS_SELECTOR, ".PageList-items-item") 
            return articles

    
    def get_article_data(self, _article, index):
        article_data = []
        #Navigate to the article
        article = _article
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".PagePromo-title"))
        )
        article, title = self.article_getter.get_title(article, index)
        date = self.article_getter.get_date(article)
        description = self.article_getter.get_description(article, index)
        image_url = self.article_getter.get_image_url(article)

        full_text = title + description

        count_phrases = full_text.lower().count(self.search_phrase.lower())

        contains_money = bool(re.search(r'\$\d+(\.\d{2})?|(\d+ (dollars|USD))', full_text))

        article_data = [title, date, description, image_url, count_phrases, contains_money]

        return article_data
        

    