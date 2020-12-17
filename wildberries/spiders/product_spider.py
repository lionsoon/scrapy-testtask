import scrapy
import logging
from wildberries.moscow_headers import headers, cookies
from wildberries.product_builder import form_product

logger = logging.getLogger(__name__)


def common_request(url, callback, meta=None):
    return scrapy.Request(url=url, callback=callback, headers=headers, cookies=cookies, meta=meta)


class QuotesSpider(scrapy.Spider):
    name = "products"

    def start_requests(self):
        yield common_request(url='https://www.wildberries.ru/catalog/obuv/zhenskaya/sabo-i-myuli/myuli',
                             callback=self.parse)

    def parse_product_card(self, response: scrapy.http.Response, **kwargs):
        yield form_product(response)

    def parse(self, response: scrapy.http.Response, **kwargs):
        section: list = response.css("ul.bread-crumbs").css("span::text").getall()
        logger.debug("SECTIONS: " + str(section))
        for i, product in enumerate(response.css('div.dtList.i-dtList.j-card-item')):
            product_ref = product.css("a.ref_goods_n_p.j-open-full-product-card::attr(href)").get()
            prod_card_url = response.urljoin(product_ref)
            yield common_request(url=prod_card_url, callback=self.parse_product_card, meta={'section': section})

        next_page_ref = response.css("a.pagination-next::attr(href)").get()
        if next_page_ref is not None:
            next_page_url = response.urljoin(next_page_ref)
            yield common_request(url=next_page_url, callback=self.parse, meta={'section': section})
