import requests
import pandas as pd
import datetime as dt
from headers import headers
from time import sleep
from random import uniform

session = requests.Session()

session.headers.update(headers)
page = 1
url = f"https://www.wildberries.ru/__internal/u-catalog/brands/v4/catalog?ab_testing=false&ab_testing=false&appType=1&brand=4126&curr=rub&dest=-1255987&hide_dtype=11&lang=ru&page={page}&sort=popular&spp=30"
response = session.get(url)
print("Status Code:", response.status_code)
items = []

while response.status_code == 200 and page <= 100:
    data = response.json()
    products = data.get('products')
    for p in products:
        item = {
            "id": p.get('id'),
            "name": p.get('name'),
            "brandId": p.get('brandId'),
            "brand": p.get('brand'),
            "entity": p.get('entity'),
            "reviewRating": p.get('reviewRating'),
            "basicPrice": p.get('sizes')[0].get('price').get('basic') / 100,
            "actualPrice": p.get('sizes')[0].get('price').get('product') / 100,
            "date": dt.date.today()
        }
        items.append(item)
    sleeptime = uniform(0.01, 0.05)
    sleep(sleeptime)
    page += 1
    url = f"https://www.wildberries.ru/__internal/u-catalog/brands/v4/catalog?ab_testing=false&ab_testing=false&appType=1&brand=4126&curr=rub&dest=-1255987&hide_dtype=11&lang=ru&page={page}&sort=popular&spp=30"
    print("Page: ", page)
    print("Status Code:", response.status_code)
df = pd.DataFrame(items)
df.to_csv("test.csv", index=False)