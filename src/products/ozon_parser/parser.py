import os
import time
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from urllib.parse import urlencode

from products.ozon_parser.scraper import ProductLinksScraper, ProductScraper


class OzonProductParser:
    product_scraper = ProductScraper()

    def parse(self, url):
        response = self.product_scraper.scrap(url)
        discount = response.find(
            "div", {"class": "b10-b0 tsBodyControl400Small"}
        ).get_text()
        price = response.find("span", {"class": "x3l lx4 x7l"}).get_text()
        description = response.select_one("#section-description .RA-a1").get_text()
        image_url = response.select_one(".j8v vj8 > .v8j .jv9 .b900-a").get("src")
        name = response.find("h1", {"class": ".yl .tsHeadline550Medium"}).get_text()
        pprint(
            {
                "name": name,
                "description": description,
                "image_url": image_url,
                "price": price,
                "discount": discount,
            }
        )


class OzonParser:
    links_scraper = ProductLinksScraper()
    product_parser = OzonProductParser()

    def __init__(self, products_count):
        self.products_count = products_count

    def parse(self):
        query_params = {"page": 1}
        product_links = []
        while self.products_count > 0:
            pprint(self.links_scraper.URL + urlencode(query_params))
            response = self.links_scraper.scrap(
                self.links_scraper.URL + urlencode(query_params)
            )
            self.products_count -= self.links_scraper.PRODUCTS_PER_PAGE
            product_links.extend(
                element.get("href") for element in response.css.select(".iy5 > a")
            )
            query_params["page"] += 3

        product_links = product_links[: self.products_count]

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(self.product_parser.parse, product_links)


if __name__ == "__main__":
    ozon = OzonParser(50)
    ozon.parse()
