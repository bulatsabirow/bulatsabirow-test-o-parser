import os
import re
import time
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor, wait
from pprint import pprint
from urllib.parse import urlencode

from urllib3.exceptions import MaxRetryError

from products.ozon_parser.scraper import ProductLinksScraper, ProductScraper


class OzonProductParser:
    def __init__(self):
        self.product_scraper = ProductScraper()

    def clean_data(self, data):
        price = re.search(r"(?P<price>.+)(?=\u2009₽)", data["price"]).group("price")
        price = price.replace("\u2009", "")
        data["price"] = price
        data["discount"] = re.search(
            r"(?<=−)(?P<discount>\d+)(?=%)", data["discount"]
        ).group("discount")
        return data

    def parse(self, url):
        try:
            response = self.product_scraper.scrap(url)
            discount = response.find(
                "div", {"class": "b10-b0 tsBodyControl400Small"}
            ).get_text()
            price = response.find("span", {"class": "x3l lx4 x7l"}).get_text()
            description = response.select_one("#section-description .RA-a1").get_text()
            image_url = response.select_one(".j8v.vj8 > .v8j.jv9.b900-a").get("src")
            name = response.find("h1", {"class": "yl tsHeadline550Medium"}).get_text()
            time.sleep(3)
            # TODO relocate to model field
            return self.clean_data(
                {
                    "name": name,
                    "description": description,
                    "image_url": image_url,
                    "price": price,
                    "discount": discount,
                }
            )
        except MaxRetryError:
            return self.parse(url)


class OzonParser:
    base_url = "https://www.ozon.ru"

    def __init__(self, products_count):
        self.links_scraper = ProductLinksScraper()
        self.product_parser = OzonProductParser()
        self.products_count = products_count

    def parse(self):
        query_params = {"page": 1}
        product_links = []
        try:
            while self.products_count > 0:
                pprint(self.links_scraper.URL + urlencode(query_params))
                response = self.links_scraper.scrap(
                    self.links_scraper.URL + urlencode(query_params)
                )
                self.products_count -= self.links_scraper.PRODUCTS_PER_PAGE
                product_links.extend(
                    self.base_url + element.get("href")
                    for element in response.css.select(".iy5 > a")
                )
                query_params["page"] += 3

            product_links = product_links[: self.products_count]
            with ThreadPoolExecutor(max_workers=2) as executor:
                tasks = [
                    executor.submit(self.product_parser.parse, product_link)
                    for product_link in product_links
                ]
            return [task.result() for task in tasks]
        finally:
            self.product_parser.product_scraper.driver.quit()
            self.links_scraper.driver.quit()


# if __name__ == "__main__":
#     ozon_parser = OzonParser(10)
#     pprint(ozon_parser.parse())
