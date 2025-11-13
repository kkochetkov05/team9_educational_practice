from brands_urls import brands_urls

def extract_brand_names(brand_urls):
    brands = set()
    for url in brands_urls:
        brands.add(url.split('/')[-1])
    return brands

brands = extract_brand_names(brands_urls)