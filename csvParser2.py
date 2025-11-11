import subprocess
import json
import csv
import time
from datetime import datetime
from pathlib import Path

# --- Настройки ---
NM_LIST_FILE = "../team9_educational_practice/nm_list.txt"   # список артикулов по одному на строку
OUT_CSV = "wb_products_full2.csv"
RETRY = 2
RETRY_DELAY = 1
TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# --- Утилиты ---
def run_curl(url: str):
    """Выполнить curl и вернуть (returncode, stdout, stderr)"""
    cmd = [
        "curl",
        "-s",
        "--max-time", str(TIMEOUT),
        "-A", USER_AGENT,
        url
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr

def fetch_product_data(nm: str):
    """
    Получаем JSON с данными товара (цена, остаток, отзывы)
    Используем рабочий эндпоинт Wildberries
    """
    # Обычно цены приходят отсюда
    url = f"https://basket-01.wb.ru/vol2646/part264676/{nm}/info/ru/card.json"

    attempt = 0
    while attempt <= RETRY:
        attempt += 1
        code, out, err = run_curl(url)
        if code == 0 and out.strip():
            try:
                data = json.loads(out)
            except json.JSONDecodeError:
                print(f"[{nm}] JSONDecodeError (попытка {attempt})")
                time.sleep(RETRY_DELAY)
                continue
            # проверим, что есть нужные поля
            if "data" in data and "products" in data["data"] and data["data"]["products"]:
                return data["data"]["products"][0]
            else:
                print(f"[{nm}] Пустой products в JSON")
                return None
        else:
            print(f"[{nm}] curl failed (attempt {attempt}): {err.strip()}")
            time.sleep(RETRY_DELAY)
    return None

def normalize_product(nm: str, product_json: dict):
    """
    Преобразуем данные в удобный словарь для CSV
    """
    sale_price = product_json.get("salePriceU") or product_json.get("priceU") or 0
    price_old = product_json.get("priceU") or 0
    return {
        "fetch_date": datetime.now().isoformat(timespec="seconds"),
        "nm": nm,
        "id": product_json.get("id"),
        "name": product_json.get("name"),
        "brand": product_json.get("brand"),
        "supplier": product_json.get("supplier"),
        "price": sale_price / 100,
        "price_old": price_old / 100,
        "feedbacks": product_json.get("feedbacks") or 0,
        "rating": product_json.get("rating") or 0,
        "stocks": product_json.get("stocks", []),
        "raw": json.dumps(product_json, ensure_ascii=False)[:2000]
    }

# --- Основной поток ---
def main():
    nm_path = Path(NM_LIST_FILE)
    if not nm_path.exists():
        print(f"{NM_LIST_FILE} не найден")
        return

    nm_list = [line.strip() for line in nm_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not nm_list:
        print("Список артикулов пуст")
        return

    csv_path = Path(OUT_CSV)
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0

    with csv_path.open("a", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["fetch_date","nm","id","name","brand","supplier","price","price_old","feedbacks","rating","stocks","raw"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        for nm in nm_list:
            print(f"Запрашиваю nm={nm} ...")
            product = fetch_product_data(nm)
            if product:
                row = normalize_product(nm, product)
                writer.writerow(row)
                print(f"  ✓ {row['name'][:50]!r}, цена: {row['price']}₽")
            else:
                print(f"  ✗ Для {nm} данные не получены")
                # записываем пустую строку для контроля
                writer.writerow({
                    "fetch_date": datetime.now().isoformat(timespec="seconds"),
                    "nm": nm,
                    "id": None, "name": None, "brand": None,
                    "supplier": None, "price": None, "price_old": None,
                    "feedbacks": None, "rating": None, "stocks": None, "raw": ""
                })
            time.sleep(0.6)  # чтобы не перегружать сервер

if __name__ == "__main__":
    main()
