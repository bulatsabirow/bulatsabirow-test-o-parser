import os
import time
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from urllib.parse import urlencode

from products.models import Product
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
        image_url = response.select_one(".j8v.vj8 > .v8j.jv9.b900-a").get("src")
        name = response.find("h1", {"class": "yl tsHeadline550Medium"}).get_text()
        return {
            "name": name,
            "description": description,
            "image_url": image_url,
            "price": price,
            "discount": discount,
        }


class OzonParser:
    base_url = "https://www.ozon.ru"
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
            products = []
            for finished_task in futures.as_completed(tasks):
                # TODO migrations
                products.append(Product(**finished_task.result()))

        return products


if __name__ == "__main__":
    # ozon = OzonParser(50)
    # ozon.parse()
    p = OzonProductParser()
    print(
        p.parse(
            "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-147121868/?_bctx=CAQQAQ&asb=DEgxhPQmIcDRO5aZ0CjN7k98R%252FPqJZXjYY1JjerGCDw%253D&asb2=ef3Q89SS-nwdribIpyMJFxt98dXLz1lcy1jq60NTHhG6ZfKb4BsNz9Zs2bcvkrYr&avtc=1&avte=4&avts=1714253615&hs=1"
        )
    )
