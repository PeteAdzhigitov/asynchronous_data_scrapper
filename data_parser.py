import asyncio
import json
import time

import aiohttp
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from seleniumbase import SB
from consts import UrlConsts

videocards_items = "catalog-product__name ui-link ui-link_black"
pagination_section = "pagination-widget__page"
data_page_number = 'data-page-number'


class SeleniumBaseObjectsClass:

    def __init__(self):
        self.sb = None
        self.context = None
        self.cookies = None

    def get_driver(self) -> None:
        sb = SB(uc=True, headed=True, headless=True)
        self.sb = sb

    def get_cookies(self, url='https://www.dns-shop.ru') -> None:
        with self.sb as sb_object:
            sb_object.open(url)
            cookies = sb_object.driver.get_cookies()
            self.cookies = {"Cookie": ';'.join([f"{elem['name']}={elem['value']}" for elem in cookies])}

class DataHandler:

    async def get_items_links(self, session: ClientSession, url: str) -> list:
        async with session.get(url) as response:
            result = await response.text()
            soup = BeautifulSoup(result, 'html.parser')
            get_products_ids = [elem.attrs['data-product'] for elem in soup.find_all(class_="catalog-product ui-button-widget")]
            return get_products_ids

    async def get_number_of_pages(self, session: ClientSession, url: str) -> int:
        async with session.get(url) as response:
            result = await response.text()
            soup = BeautifulSoup(result, 'html.parser')
            get_max_pages_in_pagination = max([int(elem.attrs[data_page_number]) for elem in soup.find_all(class_=pagination_section)])
            return get_max_pages_in_pagination

    async def get_cards_data(self, session: ClientSession, url: str) -> dict:
        async with session.get(url) as data:
            try:
                result = await data.json()
                return {result['data']['code']: result}
            except aiohttp.client_exception.ContentTypeError:
                pass



async def main():
    start = time.perf_counter()
    selenium_base_object = SeleniumBaseObjectsClass()
    selenium_base_object.get_driver()
    selenium_base_object.get_cookies()
    data_handler = DataHandler()
    selenium_base_object.cookies.update({'Accept': 'application/json'})
    async with aiohttp.ClientSession(headers=selenium_base_object.cookies) as session:
        # number_of_pages = data_handler.get_number_of_pages(session, UrlConsts.VIDEOKARTY_URL.value)
        # number_of_pages = await asyncio.gather(number_of_pages)
        # number_of_pages = number_of_pages[0] + 1
        get_ids_task = [data_handler.get_items_links(session, f'https://www.dns-shop.ru/search/?q=видеокарты&category=17a89aab16404e77&stock=now&p={page}') for page in range(1, 15)]
        ids = await asyncio.gather(*get_ids_task)
        ids_list = []
        for id_set in ids:
            ids_list.extend(id_set)
        tasks = [data_handler.get_cards_data(session, f'https://www.dns-shop.ru/pwa/pwa/get-product/?id={product_id}') for product_id in ids_list]
        results = await asyncio.gather(*tasks)
        print(results)
    end = time.perf_counter() - start
    print(end)

if __name__ == '__main__':
    asyncio.run(main())