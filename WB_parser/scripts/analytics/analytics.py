import matplotlib
# Не менять backend, если хотите показывать окна в своей среде.
matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

'''
Номера типов аналитики:
1 - Количество товаров по категориям
2 - Средние и медианные цены по категориям
3 - Динамика средних/медианных цен и количества товаров по дням для категории
4 - Количество товаров по брендам
5 - Средние цены по брендам
6 - Топ-20 брендов: средний reviewRating и среднее число feedbacks на товар
7 - Топ-20 категорий: средний reviewRating и среднее число feedbacks на товар
8 - Топ-10 товаров: по reviewRating и по feedbacks
'''

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', None)

# Путь к данным относительно расположения скрипта (измените при необходимости)
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw_data"

# Папка для вывода (в той же папке, где скрипт)
OUTPUT_BASE = Path(__file__).parent / "analytics_output"

# Проверки
if not DATA_DIR.exists():
    raise FileNotFoundError(f"DATA_DIR не найден: {DATA_DIR}")

# Загружаем все CSV
all_files = list(DATA_DIR.glob("*.csv"))
if not all_files:
    raise FileNotFoundError(f"В папке {DATA_DIR} нет CSV-файлов!")

dfs = []
for f in all_files:
    try:
        dfs.append(pd.read_csv(f))
    except Exception as e:
        print(f"Ошибка чтения {f}: {e}", file=sys.stderr)

if not dfs:
    raise ValueError("Не удалось загрузить ни один CSV-файл.")

data = pd.concat(dfs, ignore_index=True)

# Проверяем наличие колонки date
if "date" not in data.columns:
    raise ValueError("В данных нет колонки 'date'. Проверьте формат входных CSV.")

# Вспомогательные функции
def ensure_str_col(df: pd.DataFrame, col: str, fill_value="Не указан"):
    """Нормализует строковую колонку, возвращает DataFrame (не in-place)."""
    if col not in df.columns:
        df[col] = fill_value
    df[col] = df[col].astype(str).fillna(fill_value).str.lower().str.strip()
    df[col] = df[col].replace(['nan', 'none', '', 'null'], fill_value)
    return df

def make_output_dir(target_date: str, anal_type: str) -> Path:
    """Создаёт (если нужно) и возвращает путь для сохранения png."""
    out_dir = OUTPUT_BASE / target_date / f"analyt_{anal_type}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def save_and_show(fig, out_path):
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.show()
    plt.close(fig)

def choose_date():
    uniq = sorted(data['date'].astype(str).unique())
    print(f"Доступные даты: {uniq}")
    target_date = input("Введите дату (YYYY-MM-DD): ").strip()
    while target_date not in uniq:
        print(f"Нет данных за {target_date}. Доступные: {uniq}")
        target_date = input("Введите дату (YYYY-MM-DD): ").strip()
    return target_date

# Запрашиваем аналитику
while True:
    print("Доступные аналитики: \n1 - Количество товаров по категориям \n2 - Средние/медианные цены по категориям \n3 - Динамика цен и количество товаров по дням для категории \n4 - Количество товаров по брендам \n5 - Средние цены по брендам \n6 - Топ-20 брендов: avg reviewRating & avg feedbacks \n7 - Топ-20 категорий: avg reviewRating & avg feedbacks \n8 - Топ-10 товаров по reviewRating и feedbacks")
    num_analytics = input("Введите номер аналитики, которую хотите получить: ").strip()
    if not num_analytics.isdigit():
        print("\nОшибка: нужно ввести число от 1 до 8.\n")
    elif int(num_analytics) not in (1, 2, 3, 4, 5, 6, 7, 8):
        print("Ошибка: нужно ввести число от 1 до 8.\n")
    else:
        break

# Начинаем реализовывать аналитики
def analytics(num_anal):
    if num_anal == 1:
        # Количество товаров по категориям (для выбранной даты)
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()
        data_date = ensure_str_col(data_date, 'entity', fill_value='не указан')

        counts = data_date['entity'].value_counts()
        print(counts.head(50))

        out_dir = make_output_dir(target_date, "1_counts_by_category")
        fig = plt.figure(figsize=(12, 8))
        top = 20
        counts.head(top).plot(kind='bar')
        plt.title(f"Количество товаров по категориям за {target_date} (топ-{top})")
        plt.xlabel("Категория")
        plt.ylabel("Количество")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        out_path = out_dir / f"counts_by_category_top{top}.png"
        save_and_show(fig, out_path)

    elif num_anal == 2:
        # Средние и медианные цены по категориям (за выбранную дату), два графика на одной картинке
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()

        # Проверяем колонки цен
        for col in ['basicPrice', 'actualPrice']:
            if col not in data_date.columns:
                data_date[col] = pd.NA

        data_date = ensure_str_col(data_date, 'entity', fill_value='не указан')

        grouped = data_date.groupby('entity').agg(
            basic_mean=pd.NamedAgg(column='basicPrice', aggfunc='mean'),
            basic_median=pd.NamedAgg(column='basicPrice', aggfunc='median'),
            actual_mean=pd.NamedAgg(column='actualPrice', aggfunc='mean'),
            actual_median=pd.NamedAgg(column='actualPrice', aggfunc='median'),
            count=pd.NamedAgg(column='actualPrice', aggfunc='count')
        )

        # Сортируем по actual_mean убыв.
        grouped = grouped.sort_values('actual_mean', ascending=False)
        print(grouped.head(30).round(2))

        top = 20
        top_df = grouped.head(top)

        out_dir = make_output_dir(target_date, "2_prices_by_category")

        fig, axes = plt.subplots(2, 1, figsize=(14, 12))
        # Верхний: средние и медианы actualPrice (группы рядом)
        x = range(len(top_df))
        width = 0.35
        axes[0].bar([i - width / 2 for i in x], top_df['actual_mean'], width=width, label='actual_mean', alpha=0.8)
        axes[0].bar([i + width / 2 for i in x], top_df['actual_median'], width=width, label='actual_median', alpha=0.8)
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(top_df.index, rotation=45, ha='right')
        axes[0].set_title(f"Средняя и медианная актуальная цена по категориям за {target_date} (топ-{top})")
        axes[0].set_ylabel("Цена (actual)")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Нижний: средние и медианы basicPrice
        axes[1].bar([i - width / 2 for i in x], top_df['basic_mean'], width=width, label='basic_mean', alpha=0.8)
        axes[1].bar([i + width / 2 for i in x], top_df['basic_median'], width=width, label='basic_median', alpha=0.8)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(top_df.index, rotation=45, ha='right')
        axes[1].set_title(f"Средняя и медианная базовая цена по категориям за {target_date} (топ-{top})")
        axes[1].set_ylabel("Цена (basic)")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        out_path = out_dir / f"mean_median_prices_by_category_top{top}.png"
        save_and_show(fig, out_path)


    elif num_anal == 3:
        print("\n=== Аналитика динамики цен по дням ===")
        # нормализация категорий
        data["entity"] = data["entity"].astype(str).str.lower().str.strip()
        uniq_entity = set(data["entity"].unique())
        # запрашиваем существующую категорию

        while True:
            print(f"Доступные категории: {data["entity"].unique()}")
            entity = input("Введите название категории: ").strip().lower()
            if entity in uniq_entity:
                break
            print(f"\nКатегория '{entity}' не найдена. Повторите ввод.")

        # фильтрация
        category_data = data[data["entity"] == entity].copy()
        if category_data.empty:
            print(f"Нет данных для категории '{entity}'")
            return

        # обработка дат — БЕЗ генерации пропусков
        category_data["date"] = pd.to_datetime(category_data["date"])

        # группировка
        daily_stats = category_data.groupby("date").agg(
            avg_price=("actualPrice", "mean"),
            median_price=("actualPrice", "median"),
            item_count=("actualPrice", "count")
        )

        # сортировка по датам
        daily_stats = daily_stats.sort_index()
        print("\nДанные по дням:")
        print(daily_stats.round(2))

        # --- 3 графика на одной картинке ---
        fig, ax = plt.subplots(3, 1, figsize=(14, 12))

        # 1 — Средняя цена
        ax[0].plot(
            daily_stats.index.astype(str),
            daily_stats["avg_price"],
            marker="o",
            linewidth=2
        )

        ax[0].set_title(f'Средняя actualPrice по дням — "{entity}"')
        ax[0].set_ylabel("Средняя цена")
        ax[0].grid(True, alpha=0.3)
        ax[0].tick_params(axis='x', rotation=45)

        # 2 — Медианная цена
        ax[1].plot(
            daily_stats.index.astype(str),
            daily_stats["median_price"],
            marker="o",
            linewidth=2
        )

        ax[1].set_title("Медианная actualPrice по дням")
        ax[1].set_ylabel("Медианная цена")
        ax[1].grid(True, alpha=0.3)
        ax[1].tick_params(axis='x', rotation=45)

        # 3 — Количество товаров
        ax[2].bar(
            daily_stats.index.astype(str),
            daily_stats["item_count"]
        )

        ax[2].set_title("Количество товаров по дням")
        ax[2].set_xlabel("Дата")
        ax[2].set_ylabel("Товары")
        ax[2].grid(True, alpha=0.3)
        ax[2].tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # --- ПАПКА ДЛЯ АНАЛИТИКИ №3 ---
        base_dir = Path(__file__).parent / "analytics_output"
        out_dir = base_dir / "analytics_3_dynamic"
        out_dir.mkdir(parents=True, exist_ok=True)
        # файл сохраняем под названием категории
        out_path = out_dir / f"{entity}.png"
        # вывод и сохранение
        fig.savefig(out_path, dpi=220, bbox_inches='tight')
        plt.show()
        plt.close(fig)
        print(f"\nГрафик сохранён здесь:\n{out_path}")


    elif num_anal == 4:
        # Количество товаров по брендам (за выбранную дату)
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()
        data_date = ensure_str_col(data_date, 'brandName', fill_value='не указан')

        brand_counts = data_date['brandName'].value_counts()
        print(brand_counts.head(50))

        out_dir = make_output_dir(target_date, "4_counts_by_brand")
        fig = plt.figure(figsize=(14, 10))
        top = 20
        brand_counts.head(top).plot(kind='bar')
        plt.title(f"Топ-{top} брендов по количеству товаров за {target_date}")
        plt.xlabel("Бренд")
        plt.ylabel("Количество")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        out_path = out_dir / f"counts_by_brand_top{top}.png"
        save_and_show(fig, out_path)

    elif num_anal == 5:
        # Средние цены по брендам (за выбранную дату) — уже реализовано в вашем код, оставим схожее
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()
        data_date = ensure_str_col(data_date, 'brandName', fill_value='не указан')

        for col in ['basicPrice', 'actualPrice']:
            if col not in data_date.columns:
                data_date[col] = pd.NA

        brand_prices = data_date.groupby('brandName').agg(
            basic_mean=pd.NamedAgg(column='basicPrice', aggfunc='mean'),
            actual_mean=pd.NamedAgg(column='actualPrice', aggfunc='mean'),
            actual_min=pd.NamedAgg(column='actualPrice', aggfunc='min'),
            actual_max=pd.NamedAgg(column='actualPrice', aggfunc='max'),
            count=pd.NamedAgg(column='actualPrice', aggfunc='count')
        ).sort_values('actual_mean', ascending=False)

        print(brand_prices.head(30).round(2))

        top = 20
        out_dir = make_output_dir(target_date, "5_prices_by_brand")
        fig = plt.figure(figsize=(14, 8))
        brand_prices.head(top)['actual_mean'].plot(kind='bar', color='coral')
        plt.title(f"Топ-{top} брендов по средней актуальной цене за {target_date}")
        plt.ylabel("Средняя цена (actual)")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        out_path = out_dir / f"avg_prices_by_brand_top{top}.png"
        save_and_show(fig, out_path)

    elif num_anal == 6:
        # Топ-20 брендов: средний reviewRating и среднее число feedbacks на товар
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()
        data_date = ensure_str_col(data_date, 'brandName', fill_value='не указан')

        # Проверки колонок
        if 'reviewRating' not in data_date.columns:
            data_date['reviewRating'] = pd.NA
        if 'feedbacks' not in data_date.columns:
            data_date['feedbacks'] = pd.NA

        # Приводим к числам
        data_date['reviewRating'] = pd.to_numeric(data_date['reviewRating'], errors='coerce')
        data_date['feedbacks'] = pd.to_numeric(data_date['feedbacks'], errors='coerce')

        # Топ-20 брендов по числу товаров (популярность)
        brand_counts = data_date['brandName'].value_counts()
        top_brands = brand_counts.head(20).index.tolist()

        brand_stats = data_date[data_date['brandName'].isin(top_brands)].groupby('brandName').agg(
            avg_reviewRating=pd.NamedAgg(column='reviewRating', aggfunc='mean'),
            avg_feedbacks=pd.NamedAgg(column='feedbacks', aggfunc='mean'),
            count=pd.NamedAgg(column='feedbacks', aggfunc='count')
        ).sort_values('avg_reviewRating', ascending=False)

        print(brand_stats.round(2))

        out_dir = make_output_dir(target_date, "6_brand_rating_feedbacks")
        fig, ax1 = plt.subplots(figsize=(14, 8))

        x = range(len(brand_stats))
        width = 0.4
        ax1.bar([i - width / 2 for i in x], brand_stats['avg_reviewRating'], width=width, label='avg_reviewRating',
                alpha=0.8)
        ax1.set_ylabel('Средний reviewRating')
        ax1.set_xticks(x)
        ax1.set_xticklabels(brand_stats.index, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)

        ax2 = ax1.twinx()
        ax2.bar([i + width / 2 for i in x], brand_stats['avg_feedbacks'], width=width, label='avg_feedbacks', alpha=0.8,
                color='orange')
        ax2.set_ylabel('Среднее число feedbacks на товар')

        # легенда
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        plt.title(f"Топ-{len(brand_stats)} брендов: avg reviewRating & avg feedbacks за {target_date}")
        plt.tight_layout()
        out_path = out_dir / f"brand_avg_rating_feedbacks_top{len(brand_stats)}.png"
        save_and_show(fig, out_path)

    elif num_anal == 7:
        # Топ-20 категорий: средний reviewRating и среднее число feedbacks на товар
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()
        data_date = ensure_str_col(data_date, 'entity', fill_value='не указан')

        if 'reviewRating' not in data_date.columns:
            data_date['reviewRating'] = pd.NA
        if 'feedbacks' not in data_date.columns:
            data_date['feedbacks'] = pd.NA

        data_date['reviewRating'] = pd.to_numeric(data_date['reviewRating'], errors='coerce')
        data_date['feedbacks'] = pd.to_numeric(data_date['feedbacks'], errors='coerce')

        cat_counts = data_date['entity'].value_counts()
        top_cats = cat_counts.head(20).index.tolist()

        cat_stats = data_date[data_date['entity'].isin(top_cats)].groupby('entity').agg(
            avg_reviewRating=pd.NamedAgg(column='reviewRating', aggfunc='mean'),
            avg_feedbacks=pd.NamedAgg(column='feedbacks', aggfunc='mean'),
            count=pd.NamedAgg(column='feedbacks', aggfunc='count')
        ).sort_values('avg_reviewRating', ascending=False)

        print(cat_stats.round(2))

        out_dir = make_output_dir(target_date, "7_category_rating_feedbacks")
        fig, ax1 = plt.subplots(figsize=(14, 8))

        x = range(len(cat_stats))
        width = 0.4
        ax1.bar([i - width / 2 for i in x], cat_stats['avg_reviewRating'], width=width, label='avg_reviewRating',
                alpha=0.8)
        ax1.set_ylabel('Средний reviewRating')
        ax1.set_xticks(x)
        ax1.set_xticklabels(cat_stats.index, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)

        ax2 = ax1.twinx()
        ax2.bar([i + width / 2 for i in x], cat_stats['avg_feedbacks'], width=width, label='avg_feedbacks', alpha=0.8,
                color='orange')
        ax2.set_ylabel('Среднее число feedbacks на товар')

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        plt.title(f"Топ-{len(cat_stats)} категорий: avg reviewRating & avg feedbacks за {target_date}")
        plt.tight_layout()
        out_path = out_dir / f"category_avg_rating_feedbacks_top{len(cat_stats)}.png"
        save_and_show(fig, out_path)

    elif num_anal == 8:
        # Топ-10 конкретных товаров по reviewRating и feedbacks (2 графика на одной картинке)
        target_date = choose_date()
        data_date = data[data['date'] == target_date].copy()

        # Проверки
        for col in ['reviewRating', 'feedbacks', 'name', 'id']:
            if col not in data_date.columns:
                data_date[col] = pd.NA

        data_date['reviewRating'] = pd.to_numeric(data_date['reviewRating'], errors='coerce')
        data_date['feedbacks'] = pd.to_numeric(data_date['feedbacks'], errors='coerce')

        # Топ-10 по reviewRating (в случае равенства — по feedbacks)
        top_by_rating = data_date.sort_values(['reviewRating', 'feedbacks'], ascending=[False, False]).dropna(
            subset=['reviewRating']).head(10)
        top_by_rating = top_by_rating.set_index(top_by_rating['name'].astype(str).str[:60])  # обрезаем длинные имена

        # Топ-10 по feedbacks
        top_by_feedbacks = data_date.sort_values('feedbacks', ascending=False).dropna(subset=['feedbacks']).head(10)
        top_by_feedbacks = top_by_feedbacks.set_index(top_by_feedbacks['name'].astype(str).str[:60])

        out_dir = make_output_dir(target_date, "8_top_products_rating_feedbacks")
        fig, axes = plt.subplots(1, 2, figsize=(18, 8))

        # Слева: reviewRating
        axes[0].barh(range(len(top_by_rating)), top_by_rating['reviewRating'].values[::-1])
        axes[0].set_yticks(range(len(top_by_rating)))
        axes[0].set_yticklabels(top_by_rating.index[::-1])
        axes[0].set_title("Топ-10 товаров по reviewRating")
        axes[0].set_xlabel("reviewRating")
        axes[0].grid(True, alpha=0.3)

        # Справа: feedbacks
        axes[1].barh(range(len(top_by_feedbacks)), top_by_feedbacks['feedbacks'].values[::-1], color='orange')
        axes[1].set_yticks(range(len(top_by_feedbacks)))
        axes[1].set_yticklabels(top_by_feedbacks.index[::-1])
        axes[1].set_title("Топ-10 товаров по feedbacks")
        axes[1].set_xlabel("feedbacks")
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        out_path = out_dir / "top10_products_rating_and_feedbacks.png"
        save_and_show(fig, out_path)

    else:
        print(f"Аналитика №{num_anal} не найдена. Доступные варианты: 1, 2, 3, 4, 5, 6, 7, 8")
        num_analyt = input("Введите номер аналитики, которую хотите получить: ")
        analytics(int(num_analyt))

analytics(int(num_analytics))