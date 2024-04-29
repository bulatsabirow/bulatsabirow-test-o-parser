import os
import time
import random

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import Driver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


class BaseScraper:
    PAGE_LOADING_TIMEOUT = 60

    def __init__(self):
        self.driver = Driver(
            uc=True,
            no_sandbox=True,
            disable_gpu=True,
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
        self.driver.get(url)
        # Wait until all products' cards will be loaded
        WebDriverWait(self.driver, timeout=self.PAGE_LOADING_TIMEOUT).until(method)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        return soup


class ProductScraper(BaseScraper):
    def scrap(self, url):
        with self.driver:
            self.driver.get(url)
            print(f"{url} started!")
            try:
                WebDriverWait(self.driver, timeout=self.PAGE_LOADING_TIMEOUT).until(
                    EC.all_of(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#section-description > div.wk6 > h2")
                        ),
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "img.jw6.b900-a")),
                    )
                )
            except TimeoutException:
                pass

            try:
                self.driver.find_element(By.CSS_SELECTOR, ".j8v.vj8 > .v8j.jv9.b900-a")
            except NoSuchElementException:
                self.driver.find_element(By.CSS_SELECTOR, "img.jw6.b900-a").click()

            soup = BeautifulSoup(self.driver.page_source, "lxml")
        return soup
