import os
import random
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
        response = self.product_scraper.scrap(url)
        print(f"Start parsing {url}")
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
        return self.clean_data(
            {
                "name": name,
                "description": description,
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
            pprint(self.links_scraper.URL + urlencode(query_params))
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
        print(product_links)
        try:
            with ThreadPoolExecutor(max_workers=4) as executor:
                tasks = list(executor.map(self.parse_product, product_links))
        finally:
            self.links_scraper.driver.quit()
        return tasks


if __name__ == "__main__":
    links = [
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-147121868/?_bctx=CAQQAQ&asb=dZPm66ygHftDZvfDQb2cnw7XKUFahLt3XfWW%252FWNhCrI%253D&asb2=jbyMknRmp0pz3mKFCuOiqvZDngryVogMVXB7hVYu1d-eeZq6WW54VWrjVgX1vIjw&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/pompa-dlya-vody-pompa-pompa-dlya-vody-mehanicheskaya-proffi-759379209/?_bctx=CAQQAQ&asb=RvnAwf%252Bwn5QipHtVelNgn%252BjCSl78a6qgTrf0hl4Sih0%253D&asb2=-s2HPwVxL46nH1JTQFBJbGKD9HZcYiOw55NCnAmKqOMwlt48G63QNjQa-_Y8PonpNGD70tTm4dyiOtewwSTTTg&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/proffi-home-pesochnye-chasy-dlya-bani-148476397/?_bctx=CAQQAQ&asb=Aydpbn040QcJuGcsu873a2ibvLgCY2YJvC7uTU8hwYg%253D&asb2=09gsPCi0gD4e8y48hjrpLYW7huLxOXULIYo9fqmLMh_ks5TG7n8eJ78ctU-li9Tgx159tiNZH9y_7lmn6s-RhQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/uvlazhnitel-vozduha-ultrazvukovoy-nastolnyy-vozduhoochistitel-nochnik-svetilnik-proektor-410405337/?_bctx=CAQQAQ&asb=FoIqsBhlGQldFdvpCwAs12q9Bb0OfvYZxN1TqHmrKus%253D&asb2=8-IUg0AJa89dc8zLqbuMVN2d1Jc-2mPgYtgKA_SAJCbWxAwV6OP3M3P86n7NFYR7dE9oTx9tyc6x2-Vq_kcYMg&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/chemodan-detskiy-proffi-travel-loshadki-ph10482-167115671/?_bctx=CAQQAQ&asb=vGgt4XE3VoDmfLIgMkW3%252BGiep7bGTjuV2cWoo1Kt%252FL8SjecPyT1gvvCfNGzaoJBB&asb2=siDmAi3iKKoWTQPzxlpSB1GO_7phpjd9AKZTJvLMEdm0Pl4FqKcpVJtHupR_dKDY_wg_o4zR9m-xAel1E2GQw3MOPW2pL_qLgQ8N3xL8Eny4UhCTHKHqI-KwarCs1o0ualb8KuTRnvbgIw9SZHQYjTKUKGsDdT60wD6IYIou09PilpvpyYpnHbdMayboujdi&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/proffi-home-polka-dlya-vannoy-komnaty-pryamaya-1-yarusnaya-160912861/?_bctx=CAQQAQ&asb=Bm0Dzu%252F8wAzWN6SaPuRE6bAzrRUfgu%252FS736PoSZwVzQ%253D&asb2=1EldB2PMSf1nDPxVNkCxx5TrumGzObs0mGVfoCY5ZoueheIAr69A22Td2CaOIubviTtELKtQQuY7vjJmlmvvmA&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/otparivatel-mnogofunktsionalnyy-vertikalnyy-proffi-home-ph9065-s-veshalkoy-i-rezervuarom-1-6-l-162979557/?_bctx=CAQQAQ&asb=Gc1jHwi6jQw124mvNzZkPvak70fOSViRizU8Ki3fUtQ%253D&asb2=p82yqkzPq2-il_b6EOHqRWS6dbDYhhcoEhQunxKA9FL9h3TGxz2qv679HWOoBlkEQZksLAA86tqXKZdUR4fn6A&avtc=1&avte=1&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/dispenser-dlya-zhidkogo-myla-dozator-dlya-zhidkogo-myla-dozator-dlya-moyushchego-sredstva-157616437/?_bctx=CAQQAQ&asb=8jF3Ybr3%252F1rTBThDEc5aMt9LeIsbBH0TYb6JnhcvEG4%253D&asb2=g7KrD_duYysQG242LzvhDzYVYZrgKAYRCflHHu-s23gM0-lq8XJSGkjl8pqv2xNqW_ObJQHwqiG61MyY93DaOw&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/uvlazhnitel-vozduha-ultrazvukovoy-nastolnyy-s-parom-funktsiey-aromatizatsii-ochistitel-vozduha-463995406/?_bctx=CAQQAQ&asb=UCPjw7GgasVS5WZ4kLkRvltFyhLlfpXJ0SThlMnOIWQ%253D&asb2=IENJwjCHEvYl3_jjNDIxLlMl-_524-86oe9lEYDmKWzsylf69zQwFOR7Y4G5dUjjh3P9wGzaC6BT4UO2mIjjWQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/proffi-home-polka-dlya-vannoy-komnaty-pryamaya-1-yarusnaya-154996177/?_bctx=CAQQAQ&asb=sZiola1U84CMKIEiRd%252FXlo%252F6KMVrH%252BKaBgknGUfC%252BJ4%253D&asb2=DCVyG-V48TgweuGtVr2khqTKhxw5VW1Cn-5d5B7ZUUaift8t1j8rrtco5fLBslW1FoWD0uWkqHn4Twi4kotYmA&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/solevaya-lampa-proffi-ps0796-s-antibakterialnym-effektom-148103302/?_bctx=CAQQAQ&asb=sehb6qGUbijIQ68k%252FaCB8VfItibTgt1AvaiFDLVv3aE%253D&asb2=ShpN72N-r_Fnz2bkddacXlFmZLOJcQEbiGCtKQN2VvmLCDBmQpMZwE_mfP6nAD5MkOBMIe0AgrKisfBDHGRgUQ&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/shvabra-s-vedrom-10-l-shvabra-dlya-mytya-polov-shvabra-s-otzhimom-dlya-doma-dlya-dachi-dlya-536516705/?_bctx=CAQQAQ&asb=hAR%252B%252BftUSBmVWnxtL5AjU6swlaPJ11MdKinTFYOk9N4%253D&asb2=bsVNT6BH0jMc2kFU5ftCjhKULWCvR-PotVEDRIH9e8wcQYU9eNGgiXsdFc6D7uJsNMIE2JMwYUm8U1YnCxYbfA&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-ershik-147121867/?_bctx=CAQQAQ&asb=L0p6BueuIo9lwJ7dSQsn8eGQPz4qBfPoo%252BGOWm%252Bvw28%253D&asb2=893vqTpSsJfV415BTBNguppT7KNXAt1hrUazQBjxbhR1DaJimj97gQKnoY2iKghdVOlVt7mQAUZmCFvgDfUq7Q&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/solevaya-lampa-korzina-s-kristallami-elegant-proffi-ph11252-s-antibakterialnym-effektom-1032271871/?_bctx=CAQQAQ&asb=HNEqM%252FpxvXtfGoJXEHHkRljb%252B7mKPlRfT3%252FYiepJRlQ%253D&asb2=RyB-q5oi9c0YUB6Ape4D_KjX7k8jAhvMw-cRtjf67NuaI8DWD6ryB_2GIHjFRspdogtoWKtIUF-a2J-fBfYTjQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/french-press-chaynik-350-ml-s-kryshkoy-iz-bambuka-zavarochnyy-chaynik-steklyannyy-bamboo-244594477/?_bctx=CAQQAQ&asb=XNCSwX8Q259a6Vm61vRHFeUtyqDn0m%252FwGxyIOAmjeRw%253D&asb2=s0-avcrs1DB0tXssRpBS1x_R0NlEM4CZ1SyRlkSOZkiQPeMWa8V33-forLv94TelkDHk4kQV3EuzjYTJc_tjXg&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/mochalka-naturalnaya-iz-lyufy-254664017/?_bctx=CAQQAQ&asb=yoXUL9CTGd53gHyDnsOrljR3MFQAMyuN2RcamwB9TSM%253D&asb2=mlcMQfqXgoOEied67-oVxBKa7OJbEoEnjPgqxGMcztNObmAPJSE9WsbLRvPiXOdArqcAgwkQ--DB92soa4R-Aw&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/otparivatel-dlya-odezhdy-otparivatel-dlya-odezhdy-ruchnoy-proffi-273588363/?_bctx=CAQQAQ&asb=aMQADP8uVOjrhDcD6PBLgXEL3M1F2Dp3wV4mkA76rAk%253D&asb2=1ZaSi-AmhA1Vh14qC4_O70Q_80jdJ7X9WHVS7c-Xr2IxKYipYbB7Ss0xYlus17E01QbqmGU42F6kPvJkNIZ_vw&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/mylnitsa-mylnitsa-dlya-vannoy-mylnitsy-emerald-keramika-157619843/?_bctx=CAQQAQ&asb=%252FupZ6QKAfw27M7atg%252FIiaOUxE7ClkTisD0YlLVV%252BdE4%253D&asb2=Z3YjeC13aCfrDhwZLJULbMiQzWT8SNkwgzx8GEorh33PaxRaJLX7tcM5jH12AEAXjKrnZFoW-njgR87gZq1E3A&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/proffi-sauna-mochalka-naturalnaya-iz-lyufy-s-derevyannoy-ruchkoy-254665483/?_bctx=CAQQAQ&asb=G6DmnSKk5IAG18BUqShqegjuhDp1Zc1dtVqy0IHVgmg%253D&asb2=esWG2tNKYn20adHP89vexZ8axIJg5CMQGUCZkcx7p5K44KoM2En5mh4cVOzC4rWCoVmhhPdoylfUdRXfakN0AQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/proffi-shchetka-dlya-suhogo-massazha-vepr-kaban-254614933/?_bctx=CAQQAQ&asb=1eeBGubSyAOtHmOkw0pCvqhSPmD1TottzzKdl0UdgYA%253D&asb2=d09_9pKVFhEpU3mDuJWeQ16QSJ8LPXUjr-YJVfMAWvNlWduhuJ5U_vAMI538OBQzHB2YwFnRmaCFtkTqqtteuQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/uvlazhnitel-vozduha-proffi-ph11052-s-funktsiey-aromatizatsii-nochnika-i-antibakterialnym-effektom-463725734/?_bctx=CAQQAQ&asb=cXD%252FQTyIA6GKVY74l81weKWMiZXnEug1o3WsyuekfgA%253D&asb2=W2infSBS4g1BHjk3IGWmfuBq5Lr2RBJnRARWoA0KWtiYia6nTTA4Sl--_Qezg-vsDhVIWfRcCfZrWAR5D8xBKg&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/chemodan-detskiy-proffi-travel-balet-s-ruchkoy-abs-plastik-4-h-kolesnyy-1350139332/?_bctx=CAQQAQ&asb=21KmFGo4a9nWQbqvdu6X%252BJa47uXvGzxXfDzEVoizmtM%253D&asb2=imnl7aTFheIktiy_G6l7ny9kS_fJaULw265fQdE6XweUA6OuzYeJsoEa-_pjqOMfTTVKkm1FpFxYGc4_OQA6iY9DFB7MCkNVse7fxO3o6TrXHNDpHc-wM7KR4S7-vqTSQBdNlprV5tKE9BCXJARzWtnSuMT7mElHWKVHsIUZT8c&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-ershik-486716641/?_bctx=CAQQAQ&asb=8VyQXZALj3Vi%252F7tezAsv2jiQyHmijwS6ogZh3S3D28o%253D&asb2=nE9iWECv6FkCJw2yqBrqun5OgLrf7auCrJxQqMrjIZ_pFLNPLz9twbPoRRDFpeYgzs2ApSbe_Nc7mhBs3H5Ytw&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-157619841/?_bctx=CAQQAQ&asb=vXzwQ93VGMmbh%252Bg%252BBe8FEx%252FvK49pecr19x24VmQZdTU%253D&asb2=b-2uNhjSqwdgumbZMdvKd2yTxy3m7xc8hOJ0lCyLvTlcZAAbGc-e4pcgUg2dSVBIQ8uT-S8111pw86Qs3q-okA&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-554756670/?_bctx=CAQQAQ&asb=CoFpayOwWOn0tb7NIoetiwJ6X%252BidgQ%252FBjxW3QRBzr%252FU%253D&asb2=8qRgC8F9tQa3ffXYBQmew_KFe0j8KB7b8GOzN0w67_04alZFJ9sabnotuTZbkpn8v41ed43snJroEI1yJbi49A&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/aromatizator-maslo-dlya-bani-efirnoe-maslo-myata-500-ml-146279511/?_bctx=CAQQAQ&asb=5XqJG6%252FVVMuD1lyE%252BGa6TF3%252FoZ9NSZaPKcZ95OJcs4Y%253D&asb2=LJlyLS4TsGi02vzXz3wqeBMhJpQRPo4i7IZoq7SiKCiF6meugqzJC4Y3eeQusRT9oU0sCaN6X2bI67f_SRz0MQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/filtr-dlya-vertikalnogo-pylesosa-proffi-ph10641-844210334/?_bctx=CAQQAQ&asb=5HMNXP8BGZj39XZAMbsX%252F2VgCSfF50I2PBiOV9lcEgc%253D&asb2=3UYkx9ON4q01B7lIFmpqUYkrEq2TH9s-AbJrs3YE4-Ls1tHz6b7PzCH91Ckc01OffM2KUhquBEHVd4ncmYLJVA&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-160913394/?_bctx=CAQQAQ&asb=8hMtx23Tfmfllp9S1NY%252FA%252FSinxNNoAHDLe91VkqClEs%253D&asb2=TjB3m1QWfoB2CV8s2NlGp2Otv55wJ_wpivZOymN_A2OvIs5O_ezEUN4RlFWbwrtLjcEfUahFz_JtssAhCq62Jw&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-ershik-262769654/?_bctx=CAQQAQ&asb=to9Kb2u1BHx2uTZUDePCu5KorL%252BpcON2IQ4eS8xSq2I%253D&asb2=QnnCHngwjzvUc3ONI8Ps_tzDefI5nKsWihNb3BEIGZ5MlNbLykL_xMWrBSoffcwLu-JygrxrDtSx9Z_GJCZujA&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/chemodan-na-kolesah-chemodan-proffi-travel-ph9729-tour-vintage-plastikovyy-4-h-kolesnyy-s-kodovym-149721576/?_bctx=CAQQAQ&asb=ntt4Wz4iPomsFoy1qv915aedr4hkIX7jIE%252F2udMJz9KZHlIqd7s%252FDS%252FBQEU93enO&asb2=4v6EsuZYH-iIC6wxwMbs-ti94mR8U54t83qsqEj8MsQTRFXabAZ3jc7K9suC8qIs3nmvjZbV0yk9743Hs2vj5maB00NS8v3O1WQ5zZYn28IyxXVnkP2o1eWOCHbxUYrknvLpFf-WnEeNzimYBCBXkX4ZrCQmR8sZFUzxA-vVWnAc-vq1L5cnMWmyKhT7oTmk&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/skovoroda-proffi-home-hot-20-sm-s-antiprigarnym-pokrytiem-dlya-induktsionnyh-i-drugih-tipov-plit-1270001954/?_bctx=CAQQAQ&asb=vKUBDRWoj0uoKA0QUc5lWEoFl86s1U6ATTGZwaj01Xw%253D&asb2=Ec8LkpgRizNzYoR7abzI90BO6UlpQxj2MW2v659tujxFsyU50fPfo7mdiqJs5tHaaO3yIHnU2zq6CGnegLZkNQ&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/nabor-nera-filtrov-dlya-pylesosa-ph8966-3-shtuki-544881334/?_bctx=CAQQAQ&asb=I%252FyT1Wl7Oa55kI%252B3lqXw6O2Zvo1GhZFojUIzuilB4MM%253D&asb2=PdtHpnn18fKWJ9q-_M3d9qNSxJx2BglCOQp-J1Rih-eshAa5J_BtAe7wrCga8EIg4OXFlj3yUhJUT8Wgv0FKgg&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/skovoroda-gril-dlya-induktsionnoy-plity-s-antiprigarnym-pokrytiem-iz-litogo-alyuminiya-28-sm-269028438/?_bctx=CAQQAQ&asb=MBgR1eSEQP10BkndlvWAaZAFBPUXQexFswqjymLrsxI%253D&asb2=s4p_3-Vu3JwTvLcc0naSbikDSe9zMDsCW7AYuO0cPvn3paHx7kl8YKoKshTMJ5Ub1WNZPBRMrtwwsuf5-_Cy2A&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/chemodan-detskiy-proffi-travel-sovyata-ph10148-167115666/?_bctx=CAQQAQ&asb=jVVzAf5vfjuf1cLdWpX6M8aru3H1F8HJhvPWjZH5ubE%253D&asb2=kMjk4sOJoZ-lbQuc-RArtedJNLOlicaJGPNjOcq700YFDvCp0Kc4Q_a2O1Bvcui0kOHPivMcUWIVQqZf4Xg6GA&avtc=1&avte=4&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/aromatizator-maslo-dlya-bani-efirnoe-maslo-evkalipt-500-ml-146279515/?_bctx=CAQQAQ&asb=fVRhA37qxInJr%252F6tdwYSyggWgqhLQoezqccSkoBbQD0%253D&asb2=mXay3J6QfiKVNbWAlwMf51PusUYqWxCFitU-5QPb5_bphh2Jh5297X19i6bcnE8yxNv8cRW80AnqH69DgBIRGg&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/chemodan-proffi-travel-zoopark-ph10150-167118895/?_bctx=CAQQAQ&asb=xL1N6FaEHBReK3sz8qNWOJTFkhNmSQcnEWbbpOCjwBw%253D&asb2=sZy70J6kD5LuXE4bevV0HEOXw2Tp292D0Ub3hwRAgcGL5GHA7yDzonqae-CdDB9zRC1RtWC5nMt0obt2tLBRcw&avtc=1&avte=2&avts=1714375616&hs=1",
        "https://www.ozon.ru/product/chemodan-detskiy-proffi-travel-schastlivye-zveryata-s-ruchkoy-abs-plastik-4-h-kolesnyy-1350343674/?_bctx=CAQQAQ&asb=PHDyWXb3%252B0wbouQ4TX0x2tmXoHpcq4RxbzCgjXhyE1AN5rPnBoMh0fxqrNYWo%252FWZ&asb2=wehisu3FS27ZQExKCGlUKkkxZ98ocE0LieemFI0FAznV49ZiPQ6wVq7-3oOJwd8W_ja_gCbkgx0CJpLr8pFI6zxxBcFqKg3qcinsS7MkQiDgKJzIZF0I17GoFGcWuSUOKqdhbxKR_9CTrcjCne7L3oRzVr2oH1uwhZVhtRdWN_Lkt9FPN1xfI_hLh-DNSbmv&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/chemodan-na-kolesah-chemodan-proffi-travel-ph11067-tour-basic-tekstilnyy-2-h-kolesnyy-siniy-515272319/?_bctx=CAQQAQ&asb=G3ITr%252B3ZbTKkBg4oEMkz7C3rwC3vAy3qTB6aDD4Mk89FXmRcACln87CUO69178NR&asb2=DpFzJEnGwVSbSfa0a8SPHzi6dKWFAri4UmPsXXtmar6CN8GOPimbm5G3AsEoWcTX-Ri-JMYhqE1ftMLultyUO-Wk0BuWJGHzNeiOYXY1mdu1GVrKfBtUh8vZUHdsGSiyhcp3bTQPUrdx6xB8SS2p89lyWUccC3ZWZ687CS0TrHPCVAzhSkLEovEfqufY_gi7&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/stakan-dlya-zubnyh-shchetok-detskiy-stakany-stakan-dlya-vannoy-komnaty-stakan-dlya-vannoy-1338853329/?_bctx=CAQQAQ&asb=A3KNPNFaZSYmH5K3CQwaaxpI7JKgLms4vkyJAr8dKgY%253D&asb2=Xaz7LYc0meocjmYNP-mMfwH11bXe-Bc10IYHmMso_PidK7prsiDMo1XfgcMCRXMbGU8EdUrOiiySejKLKfGhQw&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-ershik-262720922/?_bctx=CAQQAQ&asb=C9S2pyulvDTpU8IqGY51GxgeMzR51e8TKydZ3xghcKI%253D&asb2=TTI0dbB8-0j8qIv95w-YaUZDN5ckEjxTqArNyzsEtd6TqBIHbObKvsQouflh_txPFqIdQvONpI0NRJXaXxhSzg&avtc=1&avte=4&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/chemodan-na-kolesah-chemodan-proffi-travel-ph11586-tour-basic-tekstilnyy-2-h-kolesnyy-korallovyy-1299887639/?_bctx=CAQQAQ&asb=hUc%252BjhAxUSfWWqLinYTWKYQNY%252F1Nz%252F8YEoeEqCufwZ5A%252FAAlUPFNW7FZAVLvoahl&asb2=mAWaSBzF6OI3DduUyjNVkZT2VLKJxq6hxMk1COyXBnXnfxoSxnRp0sqNa5gaMjbe4NT0NbXj7OZIRMydkPEQcAjqDO8U0lD8gSgbN5R97sGMPMdzzMTElrdIl3xszFHtAOepy6onGGYdHShZFnzdQBpw1VZ9sW2jxV47SQ7k8MM5mU6YKLFv-x9ruT_Uu1XD&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/chemodan-plastikovyy-na-kolesah-chemodan-proffi-travel-panorama-iz-abs-plastika-4-h-kolesnyy-168312519/?_bctx=CAQQAQ&asb=SBGflD5KQWnBXjnQODyAclND%252FUOxWMJkcCnF%252B8PScmc%253D&asb2=Gf__gdBhreFUEsKUGAmSGolWuV7L3wurz12C49G9tv84Kj6wYxmnqV8CIihiTqd0UioaJBVeYvZOeb2SowPYKEKYC8jCKolhQikB_45fF2vOap2C21hhMb_wkFD5Rybitb90s47JpTECtKGf5IwErEIcnD-LNB-e_slLwvj-O_Q&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/chemodan-na-kolesah-chemodan-proffi-travel-ph11582-tour-basic-tekstilnyy-2-h-kolesnyy-korichnevyy-1299821515/?_bctx=CAQQAQ&asb=r99UEIlkumozkW06Y8BVZjamcN9T5Jk80wVQuW6AV9yoRgaDkaQNF2s4r5VSMKSW&asb2=zG270YkfUwR57vlpDiDqumsXagfnCR4dGoijChT_XJKSW-ePjq48kpiHABdWZmS1TdP_EXnBbjiU8yjT-D17q1wA1QJKottXBuJpU4xR79ZeCaLR0qn39aANyxB1IMqK-G7GIhUe5z1qYBz78OJTKPWBYF0Zzz86CQVdc_fPClKt-IqptlDloM_-Z4NIFqEG&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/chemodan-chemodan-na-kolesah-proffi-travel-ph9658-tour-space-plastikovyy-4-h-kolesnyy-chernyy-150152533/?_bctx=CAQQAQ&asb=v710Bl%252FXCflaZD2Bm%252BJjf7XaqgL3j1sknCSG%252B8LmM1GLTSvpg3Q0ao0a7pPFgJOd&asb2=jNbNUmgSQtklfeF9UQ0uDrDAy_lWL1sP5J_hrD1soC8IvM8533AtSow_i97gb7Zm5XnLld2Vj5k9Mjowa_VO9dXA4KykKn-bUIjf9FHyQjco3CVHwDdtWmAVCb1BidulXtAYq-_-ieTtJ9pgq99ROWxIqJr59L3g9PWPitzvqirSuwL9RDRHtmuyPw8HwHOS&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/dispenser-dlya-myla-dispenser-dispenser-dlya-moyushchego-sredstva-na-kuhnyu-dispenser-dlya-1365001964/?_bctx=CAQQAQ&asb=cnnJ%252BS42I5hb%252FTdeH2AITuQ54Kf9CsW2I4LVd2YhOjc%253D&asb2=DfwoW6pmHBEovyI6Ko8XHuTdLiShorUPxfdk3aY-2orrzvpOESi0PJKZCBbPWpyxdUQMDDx1lPmDV1sUKnlr8A&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/dozator-dlya-zhidkogo-myla-matt-249361531/?_bctx=CAQQAQ&asb=PLmuV2wV0b9%252F%252Blt3y8fy4fRZ3EKwECPPScf8zf7b%252BdE%253D&asb2=F3FjKTHTAfeAv_xQ40BxAzhZFiVTRKV1AF6uOzSIn0mLgCdYYdcsl91yi37odVYPSsWlqeBlWGYnN80JYjkboQ&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/chemodan-proffi-travel-panorama-iz-abs-plastika-4-h-kolesnyy-glazunya-malyy-s-168285220/?_bctx=CAQQAQ&asb=g9OfE%252FviZZA24qvHRmkmmFd9HGzQC7XR8mzmp44IK0zoMwRsGDV4PB5OvuumsoiH&asb2=Qr6YsdWWf5BCjF7nM5lgQfY9OwX3DBG-Bk03JM5K7Dham_PBuXDFuQt7OinVE44LKcV5LmZDXA4I3K2LF3WgrT-elACVAQKIOQdYOK5t4WtqOVxfgorNznep5oqI6I4IX6a4mgoasMGHtORUOfLigs_TrUEP_v1oBwi0BPyANscp1U95saTIMutUbLfh1nzi&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/mylnitsa-mylnitsa-dlya-vannoy-mylnitsy-mylnitsa-dlya-kuskovogo-myla-mylnitsa-dlya-vannoy-mylnitsy-1364894784/?_bctx=CAQQAQ&asb=6dxXeZZETl9VnQVhIZ6ObX%252Bit8l8PdgFHWwX67BtOec%253D&asb2=0bOMjN5IlYslzYp3aDWRwGpU6lZRI7NFJ_eOUWxVkAB7a-Mm95mp0jHuvsK2QokGzbxtJQ6N3BykK6yge-AvRQ&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/stakan-dlya-zubnyh-shchetok-stakany-stakan-dlya-vannoy-komnaty-stakan-dlya-vannoy-stakany-653475563/?_bctx=CAQQAQ&asb=mcJsGm2hmjNi8PkNDcnI7J9dpMo0FIxrEaHYeM5cGbA%253D&asb2=JdsR3rKLmD07CVLIEnxKM2Zz500ET9MSSwhu-9bQ9UEPmi3q6qOC8gRnOlh4ZeEn7HbzxmclaEQMer_dhDJDYQ&avtc=1&avte=2&avts=1714375618&hs=1",
        "https://www.ozon.ru/product/ersh-dlya-unitaza-ersh-ersh-dlya-unitaza-napolnyy-ershiki-dlya-unitaza-ershik-dlya-unitaza-238448447/?_bctx=CAQQAQ&asb=f%252F42APHir5igSBlS1TYqvS33e9R%252Br%252F%252BP9jDQTwQy2qI%253D&asb2=hFKj2oltWhRSBYTMJ7M8J2LPT3oVc7gxd3C0LOZ-HkL2nlZxbBUF5NXBib7n38SF3Kr1RfX4SnAwchJJGyEbyA&avtc=1&avte=2&avts=1714375618&hs=1",
    ]
    # for link in links:
    #     OzonProductParser().parse(link)
    OzonProductParser().parse(
        "https://www.ozon.ru/product/chemodan-chemodan-na-kolesah-proffi-travel-ph9658-tour-space-plastikovyy-4-h-kolesnyy-chernyy-150152533/?_bctx=CAQQAQ&asb=xpk8VHizLEJLYPv8hQTnHRfVMksiNpdP605U5BdTrH37AwvbvzFUV5lMMfnrPN0o&asb2=bi5PntuCz-Ar7XL7oaV0LPRJTGgzLll1-fRbHllm1moMWGzMGcYBHYZTEYNrZmRW5p47zBgsJ0IJV-Qh1qXdQulzkV5gLCKzdmSKGiLjUt0Ch28Tu_nvCRFKsn5ZTskCE2iVJt_A_Enae0OSuja-ShDso3oYv8-X1XNqvrAw6j7CI9Rk6R-Iyc_VbQnQZd8A&avtc=1&avte=2&avts=1714389278&hs=1"
    )
