from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from JohnLewis.items import JohnlewisItem

import re


class JlSpider(CrawlSpider):
    name = "JL"
    use_google_cache = True

    start_urls = [
        f"https://www.johnlewis.com/browse/women/womens-dresses/_/N-flw?page={n}"
        for n in range(2, 4)
    ] + ["https://www.johnlewis.com/browse/women/womens-dresses/_/N-flw"]

    rules = (
        Rule(
            LinkExtractor(
                allow=(r"/p\d{7}"),
                deny=(
                    "home-garden",
                    "furniture-lights",
                    "electricals",
                    "women",
                    "men",
                    "beauty",
                    "gifts",
                    "sale",
                    "brands",
                    "baby-child",
                    "sport-leisure",
                ),
            ),
            callback="parse_item",
            follow=False,
        ),
    )

    def parse_item(self, response):
        item = JohnlewisItem()

        item["Description"] = (
            response.css("h1::text").get().split(",")[0]
        )  # includes brand and colour where it's given
        # item['description'] = response.css('#confirmation-anchor-desktop::text').extract() # alternative selector
        item["Category"] = "jeans"
        item["Url"] = response.url.split("//")[-1]

        if response.css(".ProductPrice_price__DcrIr > span::text").get():
            item["Price"] = response.css(".ProductPrice_price__DcrIr > span::text").get().lstrip("£")

        for text in response.css(".KeyAttributes_attribute__1O7Eo::text").extract():
            if "%" in text:

                item["Composition"] = text
                materials = [
                    "polyester",
                    "elastane",
                    "viscose",
                    "polyamide",
                    "cotton",
                    "linen",
                    "triacetate",
                    "lyocell",
                    "velvet",
                    "lace",
                    "wool",
                    "silk",
                    "satin",
                    "chiffon",
                    "leather",
                    "polyurethane",
                    "suede",
                    "spandex",
                    "acrylic",
                    "nylon",
                    "cashmere",
                    "cupro",
                    "rayon",
                    "modal",
                    "acetate",
                ]

                # option to use.split() here to take the lining composition separately
                for m in materials:
                    item[m.capitalize()] = (
                        re.findall(f"(\d{{1,3}})%\s{m}", text, re.I)[0]
                        if m in text
                        else "0"
                    )

                if "LENZING" in text:
                    item["Lenzing_Ecovero"] = re.findall(
                        r"(\d{1,3})%\sLENZING", text, re.I
                    )
                elif "lenzing" in text:
                    item["Lenzing_Ecovero"] = re.findall(
                        r"(\d{1,3})%\slenzing", text, re.I
                    )
                elif "ECOVERO" in text:
                    item["Lenzing_Ecovero"] = re.findall(
                        r"(\d{1,3})%\sECOVERO", text, re.I
                    )

                break

        yield item
