import json
import re
import requests
from bs4 import BeautifulSoup
from core.consts import UrlConsts
from seleniumbase import SB

videocards_items = "catalog-product__name ui-link ui-link_black"
pagination_section = "pagination-widget__page"
data_page_number = 'data-page-number'


class SeleniumBaseObjectsClass:

    def __init__(self):
        self.sb = None
        self.context = None
        self.cookies = None

    def get_driver(self) -> None:
        sb = SB(uc=True, headed=True)
        self.sb = sb

    def get_cookies(self, url='https://www.dns-shop.ru') -> None:
        with self.sb as sb_object:
            sb_object.open(url)
            cookies = sb_object.driver.get_cookies()
            self.cookies = {"Cookie": ';'.join([f"{elem['name']}={elem['value']}" for elem in cookies])}

class DataHandler:

    def get_items_links(self, selenium_base_object: SeleniumBaseObjectsClass,
                        url_params=lambda page: f'?stock=now&p={page}') -> list:
        result = []
        max_pages = self.get_number_of_pages(selenium_base_object)
        page = 1
        # Getting the first page
        while max_pages >= page:
            videokarty_page = requests.get(f'https://www.dns-shop.ru/search/?q=видеокарты&category=17a89aab16404e77&stock=now&p={page}',
                                           headers=selenium_base_object.cookies)
            soup = BeautifulSoup(videokarty_page.text, 'html.parser')
            get_products_ids = [elem.attrs['data-product'] for elem in soup.find_all(class_="catalog-product ui-button-widget")]
            result.extend(get_products_ids)
            page += 1
        return result

    def get_number_of_pages(self, selenium_base_object: SeleniumBaseObjectsClass,
                            url_params=lambda page: f'?stock=now&p={page}') -> int:
        page = 1
        videokarty_page = requests.get(UrlConsts.VIDEOKARTY_URL.value + url_params(page), headers=selenium_base_object.cookies)
        soup = BeautifulSoup(videokarty_page.text, 'html.parser')
        get_max_pages_in_pagination = max([int(elem.attrs[data_page_number]) for elem in soup.find_all(class_=pagination_section)])
        return get_max_pages_in_pagination

    def get_cards_data(self, products_links: list, selenium_base_object: SeleniumBaseObjectsClass):
        hash_map = {}
        for product_id in products_links:
            data = json.loads(requests.get(f'https://www.dns-shop.ru/pwa/pwa/get-product/?id={product_id}',
                                           headers=selenium_base_object.cookies).content)['data']
            hash_map[data['code']] = data
        return hash_map


def main():
    selenium_base_object = SeleniumBaseObjectsClass()
    selenium_base_object.get_driver()
    selenium_base_object.get_cookies()
    data_handler = DataHandler()
    links = data_handler.get_items_links(selenium_base_object)
    print(data_handler.get_cards_data(links, selenium_base_object))

if __name__ == '__main__':
    main()