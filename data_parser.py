import asyncio
import json
import time
import random
from collections import deque

from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential
import aiohttp
import requests
from aiohttp import ClientSession, ContentTypeError, ClientResponseError
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
            new_random_user_agent = random.choice(UserAgent().random)
            self.headers = {"User-Agent": new_random_user_agent, 'Accept': 'application/json', **self.cookies}

class DataHandler:

    async def get_items_links(self, session: ClientSession, url: str) -> list:
        async with session.get(url) as response:
            result = await response.text()
            soup = BeautifulSoup(result, 'html.parser')
            get_products_ids = [elem.attrs['data-product'] for elem in soup.find_all(class_="catalog-product ui-button-widget")]
            return get_products_ids

    @retry(retry=retry_if_exception_type((ValueError)),
           stop=stop_after_attempt(10),
           wait=wait_exponential(multiplier=1, min=1, max=10))
    async def get_number_of_pages(self, session: ClientSession, url: str) -> int:
        async with session.get(url) as response:
            result = await response.text()
            soup = BeautifulSoup(result, 'html.parser')
            try:
                get_max_pages_in_pagination = max([int(elem.attrs[data_page_number]) for elem in soup.find_all(class_=pagination_section)])
            except ValueError:
                raise ValueError
            return get_max_pages_in_pagination

    @retry(retry=retry_if_exception_type((ClientResponseError, ContentTypeError)),
           stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10))
    async def get_cards_data(self, semaphore, session: ClientSession, url: str) -> dict|str:
        async with semaphore:
            async with session.get(url) as data:
                try:
                    result = await data.json()
                except ContentTypeError:
                    return url
                except ClientResponseError:
                    return url
                return {result['data']['code']: result}


async def main():
    selenium_base_object = SeleniumBaseObjectsClass()
    selenium_base_object.get_driver()
    selenium_base_object.get_cookies()
    start = time.perf_counter()
    data_handler = DataHandler()
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(headers=selenium_base_object.cookies, connector=connector) as session:
        number_of_pages = data_handler.get_number_of_pages(session, f'{UrlConsts.VIDEOKARTY_URL.value}&stock=now&p=1')
        number_of_pages = await asyncio.gather(number_of_pages)
        get_ids_task = [data_handler.get_items_links(session, f'{UrlConsts.VIDEOKARTY_URL.value}&stock=now&p={page}')
                        for page in range(1, number_of_pages[0] + 1)]
        ids = await asyncio.gather(*get_ids_task)
        ids_list = []
        for id_set in ids:
            ids_list.extend(id_set)
        semaphore = asyncio.Semaphore(15)
        tasks = [data_handler.get_cards_data(semaphore,
                                             session,
                                             f'https://www.dns-shop.ru/pwa/pwa/get-product/?id={product_id}') for product_id in ids_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # To think about better solution cause here I have repeated code also what
        # if another exception happens in errors list
        errors = [result for result in results if isinstance(result, str)]
        tasks = [data_handler.get_cards_data(semaphore=semaphore,
                                                session=session,
                                                url=url) for url in errors]
        new_results = await asyncio.gather(*tasks)
        results.extend(new_results)
        print(time.perf_counter() - start)
        return results


if __name__ == '__main__':
    asyncio.run(main())