import matplotlib
matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

'''
Номера типов аналитики:
1 - Количество товаров по категориям
2 - Средние цены по категориям
3 - Динамика цен и количество товаров по дням для категории
4 - Количество товаров по компаниям
5 - Средние цены по компаниям
'''

# Путь к данным относительно расположения скрипта
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw_data"

print("Доступные аналитики: \n1 - Количество товаров по категориям \n2 - Средние цены по категориям \n3 - Динамика цен и количество товаров по дням для категории \n4 - Количество товаров по компаниям \n5 - Средние цены по компаниям")
num_analytics = input("Введите номер аналитики, которую хотите получить: ")

# Ищем файлы
all_files = list(DATA_DIR.glob("*.csv"))

'''print("Найденные файлы:")
for f in all_files:
    print("  -", f)'''

if not all_files:
    raise FileNotFoundError(f"В папке {DATA_DIR} нет CSV-файлов!")

# Загружаем файлы
dfs = []

for file in all_files:
    try:
        df = pd.read_csv(file)
        dfs.append(df)
    except Exception as e:
        print(f"Ошибка чтения файла {file}: {e}")

if not dfs:
    raise ValueError("Не удалось загрузить ни один CSV-файл. Проверьте формат файлов.")

# Объединяем
data = pd.concat(dfs, ignore_index=True)

# Проверяем наличие колонки date
if "date" not in data.columns:
    raise ValueError("В данных нет колонки 'date'. Проверить формат входных CSV.")

def date():
    print(f"Доступные даты: {data['date'].unique()}")
    target_date = input("Введите дату (YYYY-MM-DD): ").strip()
    data_date = data[data["date"] == target_date].copy()
    if data_date.empty:
        raise ValueError(f"Нет данных за {target_date}. Доступные даты: {data['date'].unique()}")
    return data_date, target_date

def analytics(num_anal):

    if num_anal == 1:
        # --- Аналитика количества товаров по категориям ---
        data_date, target_date = date()
        data_date["entity"] = data_date["entity"].astype(str).str.lower().str.strip()
        category_counts = data_date["entity"].value_counts()

        print(f"\nКоличество товаров по категориям за {target_date}:")
        print(category_counts)

        top = 20
        # График
        plt.figure(figsize=(10, 6))
        category_counts[:top].plot(kind="bar")
        plt.title(f"Количество товаров по категориям за {target_date}, топ-{top}")
        plt.xlabel("Категория")
        plt.ylabel("Количество товаров")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    elif num_anal == 2:
        # --- Аналитика средних цен по категориям ---
        data_date, target_date = date()
        entity = input("Введите название категории, для которой хотите получить среднюю цену: ")
        # Получаем список доступных категорий
        available_categories = data["entity"].unique()
        if entity not in available_categories:
            print(f"Категория '{entity}' не найдена в данных.")
            return
        # Группировка
        avg_prices = data_date.groupby("entity")[["basicPrice", "actualPrice"]].mean().sort_values("actualPrice",
                                                                                                   ascending=False)
        print("\nСредние цены по категориям:")
        print(avg_prices)

        print(f"Средняя цена для категории {entity}: ", avg_prices.loc[entity, "actualPrice"])

        # --- График средних цен ---
        top = 20
        plt.figure(figsize=(10, 6))
        avg_prices[:top]["actualPrice"].plot(kind="bar")
        plt.title(f"Средняя актуальная цена по категориям за {target_date}, топ-{top}")
        plt.xlabel("Категория")
        plt.ylabel("Средняя цена (actualPrice)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    elif num_anal == 3:
        # --- Аналитика динамики цен и количества товаров по дням для категории ---
        print("\n=== Аналитика динамики цен по дням ===")

        # Нормализуем названия категорий
        data["entity"] = data["entity"].astype(str).str.lower().str.strip()

        # Получаем список доступных категорий
        available_categories = data["entity"].unique()

        entity = input("Введите название категории для анализа динамики цен: ").strip().lower()

        if entity not in available_categories:
            print(f"Категория '{entity}' не найдена в данных.")
            return

        # Фильтруем данные по выбранной категории
        category_data = data[data["entity"] == entity].copy()

        if category_data.empty:
            print(f"Нет данных для категории '{entity}'")
            return

        # Преобразуем дату в datetime для корректной сортировки
        category_data["date"] = pd.to_datetime(category_data["date"])

        # Группируем по дате и вычисляем средние цены
        daily_prices = category_data.groupby("date").agg({
            "basicPrice": "mean",
            "actualPrice": "mean",
            "entity": "count"  # количество товаров в категории за день
        }).rename(columns={"entity": "item_count"})

        # Сортируем по дате
        daily_prices = daily_prices.sort_index()

        print(f"\nДинамика цен для категории '{entity}':")
        print(daily_prices.round(2))

        # --- График динамики цен ---
        plt.figure(figsize=(12, 8))

        # Создаем subplot для цен
        plt.subplot(2, 1, 1)
        plt.plot(daily_prices.index, daily_prices["basicPrice"],
                 marker='o', linewidth=2, label='Basic Price', color='blue')
        plt.plot(daily_prices.index, daily_prices["actualPrice"],
                 marker='s', linewidth=2, label='Actual Price', color='red')
        plt.title(f'Динамика цен для категории "{entity}"')
        plt.ylabel('Цена')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        # Subplot для количества товаров - ИСПРАВЛЕННАЯ ЧАСТЬ
        plt.subplot(2, 1, 2)

        # Создаем список дат и значений только для дней с данными
        dates_with_data = daily_prices.index
        item_counts = daily_prices["item_count"]

        # Создаем бар-график только для дней с данными
        bars = plt.bar(range(len(dates_with_data)), item_counts,
                       alpha=0.7, color='green')

        # Настраиваем подписи по оси X только для дней с данными
        plt.xticks(range(len(dates_with_data)),
                   [date.strftime('%Y-%m-%d') for date in dates_with_data],
                   rotation=45)

        plt.title('Количество товаров по дням')
        plt.xlabel('Дата')
        plt.ylabel('Количество товаров')
        plt.grid(True, alpha=0.3)

        # Добавляем значения на столбцы
        for bar, count in zip(bars, item_counts):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f'{int(count)}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.show()

    elif num_anal == 4:
        # --- Аналитика количества товаров по брендам ---
        data_date, target_date = date()

        # Проверяем наличие колонки с брендами
        brand_column = 'brandName'

        # Нормализуем названия брендов
        data_date[brand_column] = data_date[brand_column].astype(str).str.lower().str.strip()

        # Заменяем пустые или некорректные значения
        data_date[brand_column] = data_date[brand_column].replace(['nan', 'none', '', 'null'], 'Не указан')

        # Считаем количество товаров по брендам
        brand_counts = data_date[brand_column].value_counts()

        print(f"\nКоличество товаров по брендам за {target_date}:")
        print(f"Всего брендов: {len(brand_counts)}")
        print(brand_counts.head(20))  # Показываем топ-20

        # --- График количества товаров по брендам ---
        plt.figure(figsize=(12, 8))

        # Топ-20 брендов по количеству товаров
        top_brands = brand_counts.head(20)

        bars = plt.bar(range(len(top_brands)), top_brands.values, color='skyblue', alpha=0.7)
        plt.title(f'Топ-20 брендов по количеству товаров за {target_date}')
        plt.xlabel('Бренд')
        plt.ylabel('Количество товаров')
        plt.xticks(range(len(top_brands)), top_brands.index, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)

        # Добавляем значения на столбцы
        for bar, count in zip(bars, top_brands.values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f'{int(count)}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.show()

    elif num_anal == 5:
        # --- Аналитика средних цен по брендам ---
        data_date, target_date = date()

        # Проверяем наличие колонки с брендами
        brand_column = 'brandName'
        # Нормализуем названия брендов
        data_date[brand_column] = data_date[brand_column].astype(str).str.lower().str.strip()
        data_date[brand_column] = data_date[brand_column].replace(['nan', 'none', '', 'null'], 'Не указан')

        # Группируем по брендам и вычисляем средние цены
        brand_prices = data_date.groupby(brand_column).agg({
            'basicPrice': ['mean'],
            'actualPrice': ['mean', 'min', 'max']
        }).round(2)

        # Упрощаем названия колонок
        brand_prices.columns = ['basicPrice_mean', 'actualPrice_mean', 'actualPrice_min',
                                'actualPrice_max']

        # Сортируем по средней актуальной цене
        brand_prices = brand_prices.sort_values('actualPrice_mean', ascending=False)

        print(f"\nСредние цены по брендам за {target_date}:")
        print(f"Всего брендов: {len(brand_prices)}")
        with pd.option_context('display.width', 1000,
                               'display.max_columns', None,
                               'display.max_colwidth', 50):
            print(brand_prices.head(15)) # Показываем топ-15 по цене

        # --- График средних цен по брендам ---
        plt.figure(figsize=(14, 8))

        # Топ-20 брендов по средней цене
        top_brands_prices = brand_prices.head(20)

        # Создаем график для цен
        bars1 = plt.bar(range(len(top_brands_prices)), top_brands_prices['actualPrice_mean'],
                        color='lightcoral', alpha=0.7, label='Средняя цена')
        plt.title(f'Топ-20 брендов по средней цене за {target_date}')
        plt.ylabel('Средняя цена (actualPrice)')
        plt.xticks(range(len(top_brands_prices)), top_brands_prices.index, rotation=45, ha='right')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Добавляем значения цен на столбцы
        for bar, price in zip(bars1, top_brands_prices['actualPrice_mean']):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f'{price:.1f}', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        plt.show()

    else:
        print(f"Аналитика №{num_anal} не найдена. Доступные варианты: 1, 2, 3, 4, 5")


analytics(int(num_analytics))