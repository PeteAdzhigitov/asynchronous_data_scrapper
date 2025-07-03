import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from core.consts import UrlConsts
from seleniumbase import SB

class PlaywriteObject():

    def __init__(self):
        self.sb = None
        self.context = None
        self.cookies = None
    def get_driver(self):
        sb = SB(uc=True, headed=True)
        self.sb = sb

    def get_cookies(self, url='https://www.dns-shop.ru'):
        with self.sb as sb_object:
            sb_object.open(url)
            cookies = sb_object.driver.get_cookies()
            self.cookies = {"Cookie": ';'.join([f"{elem['name']}={elem['value']}" for elem in cookies])}

class DataHandler:
    def get_items_links(self, playwright_object: PlaywriteObject, url_params=lambda page: f'?stock=now&p={page}'):
        result = []
        max_pages = self.get_number_of_pages(playwright_object)
        page = 1
        # Getting the first page
        while max_pages >= page:
            videokarty_page = requests.get(UrlConsts.VIDEOKARTY_URL.value + url_params(page), headers=playwright_object.cookies)
            soup = BeautifulSoup(videokarty_page.text, 'html.parser')
            get_products_hrefs = soup.find_all(class_="catalog-product__name ui-link ui-link_black")
            [result.append(link.attrs['href']) for link in get_products_hrefs]
            page += 1
        return result

    def get_number_of_pages(self, playwright_object: PlaywriteObject, url_params=lambda page: f'?stock=now&p={page}'):
        page = 1
        videokarty_page = requests.get(UrlConsts.VIDEOKARTY_URL.value + url_params(page), headers=playwright_object.cookies)
        soup = BeautifulSoup(videokarty_page.text, 'html.parser')
        get_max_pages_in_pagination = max([int(elem.attrs['data-page-number']) for elem in soup.find_all(class_="pagination-widget__page")])
        return get_max_pages_in_pagination

def main():
    playwright_object = PlaywriteObject()
    playwright_object.get_driver()
    playwright_object.get_cookies()
    data_handler = DataHandler()
    print(data_handler.get_items_links(playwright_object))

if __name__ == '__main__':
    main()