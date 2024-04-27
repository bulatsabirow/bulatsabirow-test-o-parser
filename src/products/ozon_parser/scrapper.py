from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from products.ozon_parser.driver import BypassingAntibotChallengeChrome


class DataScrapper:
    URL = "https://www.ozon.ru/seller/1/products/"
    ITEMS_PER_PAGE = 36
    PAGE_LOADING_TIMEOUT = 15

    def __init__(self):
        self.driver = BypassingAntibotChallengeChrome(
            service=Service(ChromeDriverManager().install())
        )

    def crawl(self):
        method = (
            lambda driver: len(
                driver.find_elements(
                    By.CSS_SELECTOR, "#paginatorContent > div:nth-child(1) > div > div"
                )
            )
            == self.ITEMS_PER_PAGE
        )

        self.driver.get(self.URL)
        WebDriverWait(self.driver, timeout=self.PAGE_LOADING_TIMEOUT).until(method)
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        return soup
