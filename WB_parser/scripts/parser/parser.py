import requests
import pandas as pd
from datetime import date
import datetime as dt
from time import sleep
from pathlib import Path
from random import uniform

# Функция для брутфорса 429 ошибки (лимит запросов)
def bruteforce_429(url: str):
    # print("Код ошибки 429, ограничение по количеству запросов, подождите")
    # print("...")

    status_code = 429
    while status_code == 429:
        response = session.get(url)
        status_code = response.status_code
    return response

# Функция для парсинга
def parse():
    print("Подготовка. Окно браузера сейчас закроется")
    from get_headers import headers
    session.headers.update(headers)

    # Получаем список названий и реквест-ссылок на магазины
    from get_brands_request_urls import brands, get_brands_request_urls

    # brands = ('sela', 'tvoe')
    brands_request_urls = get_brands_request_urls(brands, session)

    items = []
    for brand in brands_request_urls:
        print(f'Парсинг магазина "{brand.get('name')}"')
        sleep(1)

        page = 0
        while True:
            page += 1
            brand_url = brand.get('url_head') + str(page) + brand.get('url_tail')

            sleep(uniform(0.001, 0.01))
            response = session.get(brand_url)

            if response.status_code == 429:
                response = bruteforce_429(brand_url)

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
                    "date": dt.date.today(),
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
            if products == []:
                break
        print(f'{page} страниц')
        print(f'Парсинг магазина "{brand.get('name')}" закончен')
        sleep(1)

    print("Парсинг закончен. Загрузка в файл")
    df = pd.DataFrame(items)
    data_file = Path(__file__).parent.parent.parent / 'data' / 'raw_data' / f"{date.today()}_data_test.csv"
    df.to_csv(data_file, index=False)
    print(f"Данные сохранены в файл {data_file}")

if __name__ == "__main__":
    # Создание сессии
    session = requests.Session()

    # Парсинг
    parse()