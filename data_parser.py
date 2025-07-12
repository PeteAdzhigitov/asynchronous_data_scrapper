import asyncio
import json
import time
import random

import aiohttp
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from seleniumbase import SB
from consts import UrlConsts
from fake_useragent import UserAgent

videocards_items = "catalog-product__name ui-link ui-link_black"
pagination_section = "pagination-widget__page"
data_page_number = 'data-page-number'


class SeleniumBaseObjectsClass:

    def __init__(self):
        self.sb = None
        self.context = None
        self.cookies = None
        self.headers = None

    def get_driver(self) -> None:
        sb = SB(uc=True, headed=True, headless=True)
        self.sb = sb

    def get_cookies(self, url='https://www.dns-shop.ru') -> None:
        with self.sb as sb_object:
            sb_object.open(url)
            cookies = sb_object.driver.get_cookies()
            self.cookies = {"Cookie": ';'.join([f"{elem['name']}={elem['value']}" for elem in cookies])}
            new_random_user_agent = UserAgent().random
            self.headers = {"User-Agent": new_random_user_agent, 'Accept': 'application/json', **self.cookies}

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

    async def get_cards_data(self, semaphore, session: ClientSession, url: str) -> dict:
        try:
            async with semaphore:
                async with session.get(url) as data:
                    result = await data.json()
                    return {result['data']['code']: result}
        except Exception as exception:
            print(f'There is an erro happend {exception}')


async def main():
    selenium_base_object = SeleniumBaseObjectsClass()
    selenium_base_object.get_driver()
    selenium_base_object.get_cookies()
    data_handler = DataHandler()
    async with aiohttp.ClientSession(headers=selenium_base_object.cookies) as session:
        number_of_pages = await asyncio.gather(data_handler.get_number_of_pages(session, f'{UrlConsts.VIDEOKARTY_URL.value}&stock=now&p=1'))
        get_ids_task = [data_handler.get_items_links(session, f'{UrlConsts.VIDEOKARTY_URL.value}&stock=now&p={page}')
                        for page in range(1, number_of_pages[0] + 1)]
        ids = await asyncio.gather(*get_ids_task)
        ids_list = []
        for id_set in ids:
            ids_list.extend(id_set)
        semaphore = asyncio.Semaphore(5)
        tasks = [data_handler.get_cards_data(semaphore, session, f'https://www.dns-shop.ru/pwa/pwa/get-product/?id={product_id}') for product_id in ids_list]
        results = await asyncio.gather(*tasks)
        return results


if __name__ == '__main__':
    asyncio.run(main())