import requests
import pandas as pd

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Cookie' : '_wbauid=992426401757770286; x_wbaas_token=1.1000.011d793432ad4fabaa6ee15bc25d5898.MTV8MzguMTA4LjE4Ny4xNzB8TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0Mi4wLjAuMCBTYWZhcmkvNTM3LjM2fDE3NjQwNjgwNDd8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzYzNDYzMjQ3.MEUCIQDcM/uZD05koVicEYjEvV4wUuZFT3LT9iR9FbSoSpPy7QIgItprImQTS34Cc6b4I8fj7t2Z9UeDRwjNWBgL01BHtEs=; _cp=1; routeb=1762952391.634.631.490619|4cbe85fb742f9006ed4b10eaae805e6b; _wbauid=2065175421762953988'
}

session.headers.update(headers)

main_page = session.get('https://www.wildberries.ru/')
print("Main page status:", main_page.status_code)

url = "https://www.wildberries.ru/__internal/u-catalog/brands/v4/catalog?ab_testing=false&ab_testing=false&appType=1&brand=4126&curr=rub&dest=-1255987&hide_dtype=11&lang=ru&page=1&sort=popular&spp=30"
response = session.get(url)
print("Status Code:", response.status_code)

#response = requests.get(url)

print("Status Code:", response.status_code)
#print("Response Text:", response.text[:500])

if response.status_code != 200:
    print("Ошибка: Сервер вернул код", response.status_code)
else:
    try:
        data = response.json()
        products = data.get('products')
        items = []
        for p in products:
            item = {
                "id" : p.get('id'),
                "brand" : p.get('brand'),
                "brandId": p.get('brandId'),
                "name" : p.get('name'),
                "entity": p.get('entity'),
                "reviewRating": p.get('reviewRating'),
                "basicPrice" : p.get('sizes')[0].get('price').get('basic')/100,
                "actualPrice": p.get('sizes')[0].get('price').get('product')/100
            }
            items.append(item)
        df = pd.DataFrame(items)
        df.to_csv("test.csv", index=False)
    except:
        print('ошибка')