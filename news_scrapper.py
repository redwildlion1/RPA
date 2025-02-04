import os
from datetime import datetime, timedelta
import sys
from selenium import webdriver
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from news_data_extractor import NewsDataExtractor
from selenium.webdriver.chrome.options import Options
from logger import SimpleLogger
from robocorp import workitems
from chromedriver_py import binary_path

class NewsScraper:
    def __init__(self, search_phrase, news_category, num_months):
        self.continue_scraping = True
        
        # Create a logger
        self.logger = SimpleLogger()

        self.logger.info("Starting the application")
        self.logger.info({search_phrase, news_category, num_months})

        svc = webdriver.ChromeService(executable_path=binary_path)

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Hides the browser window
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-extensions") # Disables extensions
        chrome_options.add_argument("--disable-infobars") # Disables the info bar
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") # Disables the automation bar
        chrome_options.add_argument("--disable-dev-shm-usage") # Disables the shared memory
        chrome_options.add_argument("--disable-gpu") # Disables the GPU
        chrome_options.add_argument("--disable-features=NetworkService") # Disables the network service
        chrome_options.add_argument("--disable-features=NetworkServiceInProcess") # Disables the network service in process


        self.driver = webdriver.Chrome(service=svc, options=chrome_options)

        # Enable Chrome DevTools Protocol and block the add that is causing the page to load slowly

        self.news_data_extractor = NewsDataExtractor(self.driver,search_phrase, news_category, num_months, self.logger)
        self.articles = []
        self.data_to_save = []
        self.excel = Files()
        self.http = HTTP()


        self.output_dir = 'output'
        self.excel_file = os.path.join(self.output_dir, 'news_data.xlsx')
        self.init_excel_file()


    def init_excel_file(self):
        self.excel.create_workbook(self.excel_file)
        self.excel.create_worksheet('News')

    def search_news(self):
        self.news_data_extractor.get_to_article_page()

    def select_category(self):
        self.news_data_extractor.select_category()

    def sort_by_newest(self):
        self.news_data_extractor.sort_by_newest()

    def extract_articles_from_this_page(self):
        if self.continue_scraping:
            self.articles += self.news_data_extractor.get_articles_from_wrapper()

    def navigate_to_next_page(self, continue_scraping):
        if continue_scraping:
            navigate = self.news_data_extractor.navigate_to_next_page()
            if not navigate:
                self.continue_scraping = False
                self.logger.info("Reached the end of the search by pages")
        

    def extract_data_from_articles(self):
        for article in self.articles:
            index = self.articles.index(article)
            article_data = self.news_data_extractor.get_article_data(article, index)
            if (datetime.strptime(article_data[1], '%Y-%m-%d') < (datetime.now() - timedelta(days=30 * self.news_data_extractor.num_months))):
                self.continue_scraping = False
                self.logger.info("Reached the end of the search by date " + article_data[1])
                break
            self.data_to_save.append(article_data)
        

    def save_to_excel(self, data):
        self.excel.append_rows_to_worksheet(data)
        self.excel.save_workbook()


    def close(self):
        self.logger.info("Closing the application")
        self.driver.quit()
        self.excel.close_workbook()

if __name__ == "__main__":
    parameters = workitems.inputs
    for item in parameters:
        search_phrase = item.payload['search_phrase'] if item.payload else "robots"
        news_category = item.payload['news_category'] if item.payload else "Stories"
        num_months = item.payload['num_months'] if item.payload else 5
    # Replace with actual parameters
    scraper = NewsScraper(search_phrase=search_phrase, news_category=news_category, num_months=num_months)
    try:
        scraper.search_news()
        scraper.sort_by_newest()
        scraper.select_category()
        while (scraper.continue_scraping):
            scraper.extract_articles_from_this_page()
            scraper.extract_data_from_articles()
            scraper.navigate_to_next_page(scraper.continue_scraping)
        scraper.save_to_excel(scraper.data_to_save)
    finally:
        scraper.close()