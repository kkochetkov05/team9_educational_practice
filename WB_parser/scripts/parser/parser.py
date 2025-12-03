"""
Скрипт выполняет функцию парсинга данных

- parse() формирует request-ссылку из полученных из get_brands_request_urls.py частей.
После обращается по ней, получает .json файл с нужной информацией,
затем переносит нужную информацию в словарь.
После обработки всех товаров сохраняет .csv данные в RAW_DATA_DIR (см. config.py).
"""


import requests
import pandas as pd
from datetime import date
from time import sleep
from random import uniform

from config import *

# Функция для брутфорса 429 ошибки (лимит запросов)
def bruteforce_429(url: str, session):
    # print("Код ошибки 429, ограничение по количеству запросов, подождите")
    # print("...")

    status_code = 429
    while status_code == 429:
        response = session.get(url)
        status_code = response.status_code
    return response

# Функция для парсинга
def parse():
    # Создание сессии
    session = requests.Session()

    print("Подготовка. Окно браузера сейчас закроется")
    from get_headers import headers
    session.headers.update(headers)

    # Получаем список названий и реквест-ссылок на магазины
    from get_brands_request_urls import brands, get_brands_request_urls

    # brands = ('sela', 'tvoe')
    brands_request_urls = get_brands_request_urls(brands, session)

    print(f"Парсинг магазинов {[brand.get('name') for brand in brands_request_urls]}")

    items = []
    for brand in brands_request_urls:
        print(f'Парсинг магазина "{brand.get('name')}"')
        sleep(1)

        page = 0
        while True:
            page += 1
            page_request_url = brand.get('url_head') + str(page) + brand.get('url_tail')

            sleep(uniform(0.001, 0.01))
            response = session.get(page_request_url)

            if response.status_code == 429:
                response = bruteforce_429(page_request_url, session)

            if response.status_code != 200 and response.status_code != 429:
                print(f"Ошибка обращения к {page} странице каталога")
                print("Код ошибки: ", response.status_code)

            try:
                data = response.json()
            except:
                break
            products = data.get('products')

            for p in products:
                item = {
                    "date": date.today(),
                    "id": p.get('id'),
                    "name": p.get('name'),
                    "brandId": p.get('brandId'),
                    "brandName": p.get('brand'),
                    "entity": p.get('entity'),
                    "reviewRating": p.get('reviewRating'),
                    "feedbacks": p.get('feedbacks'),
                    "basicPrice": int(p.get('sizes')[0].get('price').get('basic') / 100),
                    "actualPrice": int(p.get('sizes')[0].get('price').get('product') / 100),
                    "supplierId": p.get('supplierId'),
                    "supplier": p.get('supplier'),
                    "supplierRating": p.get('supplierRating'),
                    "totalQuantity": p.get('totalQuantity')
                }
                items.append(item)

            if page % 10 == 0:
                print(f'{page} страниц')
            if not products:
                break
        print(f'{page} страниц')
        print(f'Парсинг магазина "{brand.get('name')}" закончен\n')
        sleep(1)

    print("Парсинг закончен. Загрузка в файл")
    df = pd.DataFrame(items)
    data_file = RAW_DATA_DIR / f"{date.today()}_data.csv"
    df.to_csv(data_file, index=False)
    print(f"Данные сохранены в файл {data_file}\n")

if __name__ == '__main__':

    # Создание сессии
    session = requests.Session()

    # Парсинг
    parse()