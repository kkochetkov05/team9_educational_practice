import requests
import pandas as pd
import datetime as dt
from time import sleep
from pathlib import Path
import sys

def get_brand_url(brand_name: str) -> str:
    url = f"https://static-basket-01.wbbasket.ru/vol0/data/brands/{brand_name}.json"
    response = session.get(url)

    if response.status_code != 200:
        print("Ошибка обращения к странице бренда на маркетплейсе")
        print("Код ошибки: ", response.status_code)
        quit()

    brand_data = response.json()
    brand_id = brand_data.get('id')
    brand_name = brand_data.get('name')

    brand_url_head = f"https://www.wildberries.ru/__internal/u-catalog/brands/v4/catalog?ab_testing=false&ab_testing=false&appType=1&brand={brand_id}&curr=rub&dest=-1255987&hide_dtype=11&lang=ru&page="
    brand_url_tail = "&sort=popular&spp=30"

    print("Ссылка для обращения к каталогу сформирована успешно")
    return brand_url_head, brand_url_tail, brand_name

def bruteforce_429(url: str):
    print("Код ошибки 429, ограничение по количеству запросов, подождите")
    print("...")

    status_code = 429
    while status_code == 429:
        response = session.get(url)
        status_code = response.status_code
    return response

def parse(brands: tuple):
    items = []
    for brand in brands:
        # формирование ссылки обращения на первую страницу каталога
        brand_url_head, brand_url_tail, brand_name = get_brand_url(brand)

        print(f'Парсинг магазина "{brand_name}"')


        page = 0
        while True:
            page += 1
            brand_url = brand_url_head + str(page) + brand_url_tail

            response = session.get(brand_url)
            if response.status_code == 429:
                response = bruteforce_429(brand_url)
            if response.status_code != 200 and response.status_code != 429:
                print(f"Ошибка обращения к {page} странице каталога")
                print("Код ошибки: ", response.status_code)
            print(f"Парсинг {page} страницы")
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
            if products == []:
                break

        print(f'Парсинг магазина "{brand_name}" закончен')
        sleep(3)

    print("Парсинг закончен. Загрузка в файл")
    df = pd.DataFrame(items)
    data_file = Path(__file__).parent.parent / 'data' / f"{dt.date.today()}_data.csv"
    df.to_csv(data_file, index=False)

if __name__ == "__main__":
    sources_path = Path(__file__).parent.parent / 'sources'
    sys.path.insert(1, str(sources_path))

    # Создание сессии
    session = requests.Session()
    from headers import headers
    session.headers.update(headers)

    # brands = ('yunichel', 'tvoe')
    from brands import brands
    parse(brands)