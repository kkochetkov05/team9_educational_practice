import subprocess
import json
import csv
import time
from datetime import datetime
from pathlib import Path

# --- Настройки ---
NM_LIST_FILE = "../team9_educational_practice/nm_list.txt"   # файл с артиклями (по одному nmId на строку)
OUT_CSV = "wb_products.csv"
ENDPOINTS = [
    "https://card.wb.ru/cards/v2/detail",
    "https://card.wb.ru/cards/v1/detail",  # fallback
    # можно добавить другие зеркала, если надо
]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
RETRY = 2               # сколько дополнительных попыток на каждый эндпоинт
RETRY_DELAY = 2         # сек между попытками
TIMEOUT = 15            # таймаут curl (сек)

# --- Утилиты ---
def run_curl(url: str) -> (int, str, str):
    """
    Выполнить curl и вернуть (returncode, stdout, stderr)
    """
    # используем -s (silent) и --max-time (таймаут в сек)
    cmd = [
        "curl",
        "-s",
        "--max-time", str(TIMEOUT),
        "-A", USER_AGENT,
        url
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr

def fetch_product_by_nm(nm: str) -> dict | None:
    """
    Пробуем по всем эндпоинтам, возвращаем разобранный JSON (первую product) или None.
    """
    for base in ENDPOINTS:
        # формируем url (параметр nm)
        url = f"{base}?appType=1&curr=rub&dest=-1257786&nm={nm}"
        attempt = 0
        while attempt <= RETRY:
            attempt += 1
            code, out, err = run_curl(url)
            if code == 0 and out:
                # пробуем распарсить JSON
                try:
                    data = json.loads(out)
                except json.JSONDecodeError:
                    # не JSON — логим и пробуем снова
                    print(f"[{nm}] Некорректный JSON от {base} (попытка {attempt}): {out[:200]!r}")
                    time.sleep(RETRY_DELAY)
                    continue

                # Проверим структуру
                prod = data.get("data", {}).get("products")
                if prod:
                    return prod[0]  # возвращаем первый элемент
                else:
                    # пустой ответ JSON — товар отсутствует на этом эндпоинте
                    print(f"[{nm}] Нет данных в ответе от {base}.")
                    break  # переходить к следующему эндпоинту
            else:
                # curl вернул ошибку (код != 0) — лог и повтор
                print(f"[{nm}] curl failed for {base} (code={code}), err: {err.strip()[:200]!r} (attempt {attempt})")
                time.sleep(RETRY_DELAY)
        # переходим к следующему эндпоинту
    return None

def normalize_product(nm: str, product_json: dict) -> dict:
    """
    Вернёт словарь с нужными полями для CSV.
    Обрабатываем отсутствие полей безопасно.
    """
    return {
        "fetch_date": datetime.now().isoformat(timespec="seconds"),
        "nm": nm,
        "id": product_json.get("id"),
        "name": product_json.get("name"),
        "brand": product_json.get("brand"),
        "supplier": product_json.get("supplier"),
        "price": (product_json.get("salePriceU") or 0) / 100 if product_json.get("salePriceU") is not None else None,
        "price_old": (product_json.get("priceU") or 0) / 100 if product_json.get("priceU") is not None else None,
        "rating": product_json.get("rating"),
        "feedbacks": product_json.get("feedbacks"),
        "raw": json.dumps(product_json, ensure_ascii=False)[:2000]  # truncate raw if very long
    }

# --- Основной поток ---
def main():
    nm_path = Path(NM_LIST_FILE)
    if not nm_path.exists():
        print(f"Файл {NM_LIST_FILE} не найден. Создай файл с nmId по одной строке.")
        return

    nm_list = [line.strip() for line in nm_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not nm_list:
        print("Список артикулов пуст.")
        return

    # Если CSV не существует — создаём и пишем заголовок
    csv_path = Path(OUT_CSV)
    write_header = not csv_path.exists()

    with csv_path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "fetch_date", "nm", "id", "name", "brand", "supplier", "price", "price_old", "rating", "feedbacks", "raw"
        ])
        if write_header:
            writer.writeheader()

        for nm in nm_list:
            print(f"Запрашиваю nm={nm} ...")
            prod = fetch_product_by_nm(nm)
            if prod:
                row = normalize_product(nm, prod)
                writer.writerow(row)
                print(f"  ✓ Сохранено: {row['name'][:80]!r} / {row['price']}₽")
            else:
                # сохраняем запись с пустыми полями для контроля
                writer.writerow({
                    "fetch_date": datetime.now().isoformat(timespec="seconds"),
                    "nm": nm,
                    "id": None, "name": None, "brand": None,
                    "supplier": None, "price": None, "price_old": None,
                    "rating": None, "feedbacks": None, "raw": ""
                })
                print(f"  ✗ Для {nm} данные не найдены на всех эндпоинтах.")
            # небольшой дедлайн между товарами, чтобы не нагружать сеть
            time.sleep(0.6)

if __name__ == "__main__":
    main()
