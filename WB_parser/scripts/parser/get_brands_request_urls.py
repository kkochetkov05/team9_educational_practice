from pathlib import Path
import json

brands_urls_file = Path(__file__).parent.parent.parent / 'sources' / 'brands_urls.json'
with open(brands_urls_file, 'r', encoding='utf-8') as f:
    brands_urls = json.load(f)

# Достать названия брендов из ссылок на их главную страницу
def extract_brand_names(brand_urls):
    brands = set()
    for url in brands_urls:
        brands.add(url.split('/')[-1])
    return brands

brands = extract_brand_names(brands_urls)

# Сформировать ссылки для реквеста
def get_brands_request_urls(brands: list, session) -> list:
    brands_request_urls = []
    for brand_name in brands:
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

        # print("Ссылка для обращения к каталогу сформирована успешно")
        brands_request_urls.append({'name' : brand_name, 'url_head' : brand_url_head, 'url_tail' : brand_url_tail})
    return brands_request_urls

