import enum


categories_hash_map = {

    "видеокарты": "17a89aab16404e77"
}

class UrlConsts(enum.Enum):
    VIDEOKARTY_URL = 'https://www.dns-shop.ru/search/?q=видеокарты&category=17a89aab16404e77'
    TODAY = 'today'
    TOMORROW = 'tomorrow'
    NOW = 'now'
    LATER = 'later'
    OUT_OF_STOCK = 'out_of_stock'