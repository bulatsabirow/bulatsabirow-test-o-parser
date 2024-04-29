from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

from products.models import Product
from products.ozon_parser.scraper import ProductLinksScraper, ProductScraper


class OzonProductParser:
    def __init__(self):
        self.product_scraper = ProductScraper()

    def clean_data(self, data):
        return data

    def parse(self, url):
        response = self.product_scraper.scrap(url)
        discount = response.find(
            "div", {"class": "b10-b0 tsBodyControl400Small"}
        ).get_text()
        price = response.find("span", {"class": "x3l lx4 x7l"}).get_text()
        description_block = response.select_one("#section-description .RA-a1")
        description = ""
        if description_block is not None:
            description = description_block.get_text()
        image_url = response.select_one(".j8v.vj8 > .v8j.jv9.b900-a").get("src")
        name = response.find("h1", {"class": "yl tsHeadline550Medium"}).get_text()
        # TODO relocate to model field
        return Product(
            **{
                "name": name,
                "description": description,
                "url": url,
                "image_url": image_url,
                "price": price,
                "discount": discount,
            }
        )


class OzonParser:
    base_url = "https://www.ozon.ru"

    def __init__(self, products_count):
        self.links_scraper = ProductLinksScraper()
        self.products_count = products_count

    def parse_product(self, url):
        product_parser = OzonProductParser()
        return product_parser.parse(url)

    def parse(self):
        query_params = {"page": 1}
        product_links = []
        while self.products_count > 0:
            response = self.links_scraper.scrap(
                self.links_scraper.URL + urlencode(query_params)
            )
            self.products_count -= self.links_scraper.PRODUCTS_PER_PAGE
            product_links.extend(
                self.base_url + element.get("href")
                for element in response.css.select(".iy5 > a")
            )
            query_params["page"] += 1

        product_links = product_links[: self.products_count]
        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                tasks = list(executor.map(self.parse_product, product_links))
        finally:
            self.links_scraper.driver.quit()
        return tasks
