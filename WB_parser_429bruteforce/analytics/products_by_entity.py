import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

import os

# Папка с CSV-файлами
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)  # нормализуем

target_date = input("Введите дату (YYYY-MM-DD): ").strip()

# --- 1. Ищем файлы ---
all_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

print("Найденные файлы:")
for f in all_files:
    print("  -", f)

if not all_files:
    raise FileNotFoundError(f"В папке {DATA_DIR} нет CSV-файлов!")

# --- 2. Загружаем файлы ---
dfs = []

for file in all_files:
    try:
        df = pd.read_csv(file)
        dfs.append(df)
    except Exception as e:
        print(f"Ошибка чтения файла {file}: {e}")

if not dfs:
    raise ValueError("Не удалось загрузить ни один CSV-файл. Проверьте формат файлов.")

# --- 3. Объединяем ---
data = pd.concat(dfs, ignore_index=True)

# --- 4. Проверяем наличие колонки date ---
if "date" not in data.columns:
    raise ValueError("В данных нет колонки 'date'. Проверить формат входных CSV.")

# --- 5. Фильтрация по дате ---
data_date = data[data["date"] == target_date].copy()

if data_date.empty:
    raise ValueError(f"Нет данных за {target_date}. Доступные даты: {data['date'].unique()}")

# --- 6. Аналитика ---
data_date["entity"] = data_date["entity"].astype(str).str.lower().str.strip()
category_counts = data_date["entity"].value_counts()

print(f"\nКоличество товаров по категориям за {target_date}:")
print(category_counts)

# --- 7. График ---
plt.figure(figsize=(10, 6))
category_counts[:20].plot(kind="bar")
plt.title(f"Количество товаров по категориям за {target_date}")
plt.xlabel("Категория")
plt.ylabel("Количество товаров")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

