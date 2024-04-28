import time

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import Driver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


class BaseScraper:
    PAGE_LOADING_TIMEOUT = 15

    def __init__(self):
        self.driver = Driver(
            uc=True,
            headed=True,
        )

    def scrap(self, url):
        return NotImplemented


class ProductLinksScraper(BaseScraper):
    URL = "https://www.ozon.ru/seller/proffi-1/products/?miniapp=seller_1&"
    PRODUCTS_PER_PAGE = 36

    def scrap(self, url=URL):
        method = (
            lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".iy5 > a"))
            == self.PRODUCTS_PER_PAGE
        )
        with self.driver:
            self.driver.get(url)
            # Wait until all products' cards will be loaded
            WebDriverWait(self.driver, timeout=self.PAGE_LOADING_TIMEOUT).until(method)
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            return soup


class ProductScraper(BaseScraper):
    def scrap(self, url):
        with self.driver:
            self.driver.get(url)
            WebDriverWait(self.driver, timeout=self.PAGE_LOADING_TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#section-description > div.wk6 > h2")
                )
            )
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            return soup