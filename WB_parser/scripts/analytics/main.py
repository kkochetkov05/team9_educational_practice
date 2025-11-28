import matplotlib

matplotlib.use("TkAgg")

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3

from PIL import Image
import shutil

from config import *

def get_connection():
    """Создаёт подключение к базе данных"""
    if not DB_PATH:
        raise ValueError("DB_PATH пуст! Укажите путь к базе данных.")
    return sqlite3.connect(DB_PATH)


def load_data(conn):
    """Загружает все данные из таблицы wildberries_data"""
    query = "SELECT * FROM wildberries_data"
    data = pd.read_sql(query, conn)

    # Приводим числовые колонки
    for col in ['actualPrice', 'basicPrice', 'reviewRating', 'feedbacks', 'totalQuantity']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')

    return data


def ensure_str_col(df: pd.DataFrame, col: str, fill_value="не указан"):
    """Нормализует строковую колонку"""
    if col not in df.columns:
        df[col] = fill_value
    df[col] = df[col].astype(str).fillna(fill_value).str.lower().str.strip()
    df[col] = df[col].replace(['nan', 'none', '', 'null'], fill_value)
    return df


def folder_to_pdf_and_delete(folder_path):
    """
    Объединяет все JPEG-файлы в папке в один PDF-файл с названием папки,
    затем удаляет исходную папку.
    """
    folder_path = Path(folder_path)

    if not folder_path.exists():
        print(f"  ⚠️  Папка не найдена: {folder_path.name}")
        return False

    # Получаем все JPEG-файлы в папке и сортируем их
    jpg_files = sorted(folder_path.glob("*.jpg"))

    if not jpg_files:
        print(f"  ⚠️  Нет JPEG-файлов в папке: {folder_path.name}")
        shutil.rmtree(folder_path)
        return False

    try:
        # Открываем все изображения
        images = []
        for jpg_file in jpg_files:
            img = Image.open(jpg_file).convert('RGB')
            images.append(img)

        # Создаём PDF рядом с папкой
        pdf_path = folder_path.parent / f"{folder_path.name}.pdf"
        images[0].save(
            pdf_path,
            save_all=True,
            append_images=images[1:],
            quality=85,
            duration=100,
            loop=0
        )

        print(f"  ✓ PDF создан: {pdf_path.name}")

        # Удаляем исходную папку
        shutil.rmtree(folder_path)
        print(f"  ✓ Папка удалена: {folder_path.name}")

        return True

    except Exception as e:
        print(f"  ❌ Ошибка при создании PDF: {e}")
        return False

def save_plot(fig, out_path, show=True):
    """Сохраняет и показывает график"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Сохраняем в JPEG с качеством 85% через pil_kwargs
    fig.savefig(out_path, format='jpeg', dpi=100, bbox_inches='tight', pil_kwargs={'quality': 85})
    if show:
        plt.show()
    plt.close(fig)
    print(f"  ✓ Сохранено: {out_path.name}")



def set_smart_ylim(ax, data_values, margin=0.1):
    """Устанавливает умные границы оси Y с отступами"""
    data_values = [v for v in data_values if pd.notna(v)]
    if not data_values:
        return
    vmin, vmax = min(data_values), max(data_values)
    range_val = vmax - vmin
    if range_val == 0:
        range_val = vmax * 0.1 if vmax != 0 else 1
    ax.set_ylim(vmin - range_val * margin, vmax + range_val * margin)


def set_smart_xlim(ax, data_values, margin=0.1):
    """Устанавливает умные границы оси X с отступами (для горизонтальных графиков)"""
    data_values = [v for v in data_values if pd.notna(v)]
    if not data_values:
        return
    vmin, vmax = min(data_values), max(data_values)
    range_val = vmax - vmin
    if range_val == 0:
        range_val = vmax * 0.1 if vmax != 0 else 1
    ax.set_xlim(vmin - range_val * margin, vmax + range_val * margin)


# ══════════════════════════════════════════════════════════════
# ОСНОВНАЯ АНАЛИТИКА (по каждой дате отдельно)
# ══════════════════════════════════════════════════════════════

def basic_analytics_for_date(data, target_date):
    """Выполняет всю основную аналитику для одной даты"""

    data_date = data[data['date'] == target_date].copy()
    data_date = ensure_str_col(data_date, 'entity', fill_value='не указан')
    data_date = ensure_str_col(data_date, 'brandName', fill_value='не указан')

    out_dir = BASIC_OUTPUT / f"{target_date}_analytics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📊 Аналитика за {target_date}:")

    # ─── 1. Количество товаров по категориям ───
    counts = data_date['entity'].value_counts()
    fig = plt.figure(figsize=(8, 5))
    top = min(20, len(counts))
    counts.head(top).plot(kind='bar', color='steelblue')
    plt.title(f"Количество товаров по категориям (топ-{top})", fontsize=12, weight='bold')
    plt.xlabel("Категория")
    plt.ylabel("Количество")
    plt.xticks(rotation=45, ha='right')
    ax = plt.gca()
    set_smart_ylim(ax, counts.head(top).values)
    plt.tight_layout()
    save_plot(fig, out_dir / f"1_counts_by_category_top{top}.jpg", False)

    # ─── 2. Средние и медианные цены по категориям ───
    grouped = data_date.groupby('entity').agg(
        actual_mean=pd.NamedAgg(column='actualPrice', aggfunc='mean'),
        actual_median=pd.NamedAgg(column='actualPrice', aggfunc='median'),
        basic_mean=pd.NamedAgg(column='basicPrice', aggfunc='mean'),
        basic_median=pd.NamedAgg(column='basicPrice', aggfunc='median')
    ).sort_values('actual_mean', ascending=False)

    top = min(20, len(grouped))
    top_df = grouped.head(top)

    fig, axes = plt.subplots(2, 1, figsize=(8, 10))
    x = range(len(top_df))
    width = 0.35

    # actualPrice
    axes[0].bar([i - width / 2 for i in x], top_df['actual_mean'], width=width, label='Средняя', alpha=0.8)
    axes[0].bar([i + width / 2 for i in x], top_df['actual_median'], width=width, label='Медианная', alpha=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(top_df.index, rotation=45, ha='right')
    axes[0].set_title("Актуальная цена (actualPrice) по категориям", fontsize=11, weight='bold')
    axes[0].set_ylabel("Цена")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    set_smart_ylim(axes[0], list(top_df['actual_mean']) + list(top_df['actual_median']))

    # basicPrice
    axes[1].bar([i - width / 2 for i in x], top_df['basic_mean'], width=width, label='Средняя', alpha=0.8,
                color='orange')
    axes[1].bar([i + width / 2 for i in x], top_df['basic_median'], width=width, label='Медианная', alpha=0.8,
                color='coral')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(top_df.index, rotation=45, ha='right')
    axes[1].set_title("Базовая цена (basicPrice) по категориям", fontsize=11, weight='bold')
    axes[1].set_ylabel("Цена")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    set_smart_ylim(axes[1], list(top_df['basic_mean']) + list(top_df['basic_median']))

    plt.tight_layout()
    save_plot(fig, out_dir / f"2_prices_by_category_top{top}.jpg", False)

    # ─── 3. Количество товаров по брендам ───
    brand_counts = data_date['brandName'].value_counts()
    fig = plt.figure(figsize=(8, 6))
    top = min(20, len(brand_counts))
    brand_counts.head(top).plot(kind='bar', color='teal')
    plt.title(f"Топ-{top} брендов по количеству товаров", fontsize=12, weight='bold')
    plt.xlabel("Бренд")
    plt.ylabel("Количество")
    plt.xticks(rotation=45, ha='right')
    ax = plt.gca()
    set_smart_ylim(ax, brand_counts.head(top).values)
    plt.tight_layout()
    save_plot(fig, out_dir / f"3_counts_by_brand_top{top}.jpg", False)

    # ─── 4. Средние и медианные цены по брендам ───
    brand_prices = data_date.groupby('brandName').agg(
        actual_mean=pd.NamedAgg(column='actualPrice', aggfunc='mean'),
        actual_median=pd.NamedAgg(column='actualPrice', aggfunc='median'),
        count=pd.NamedAgg(column='actualPrice', aggfunc='count')
    ).sort_values('actual_mean', ascending=False)

    top = min(20, len(brand_prices))
    top_df = brand_prices.head(top)

    fig = plt.figure(figsize=(8, 5))
    x = range(len(top_df))
    width = 0.35
    plt.bar([i - width / 2 for i in x], top_df['actual_mean'], width=width, label='Средняя', alpha=0.8, color='coral')
    plt.bar([i + width / 2 for i in x], top_df['actual_median'], width=width, label='Медианная', alpha=0.8,
            color='salmon')
    plt.xticks(x, top_df.index, rotation=45, ha='right')
    plt.title(f"Топ-{top} брендов по цене (actualPrice)", fontsize=12, weight='bold')
    plt.ylabel("Цена")
    plt.legend()
    ax = plt.gca()
    set_smart_ylim(ax, list(top_df['actual_mean']) + list(top_df['actual_median']))
    plt.tight_layout()
    save_plot(fig, out_dir / f"4_prices_by_brand_top{top}.jpg", False)

    # ─── 5. Топ-20 брендов: reviewRating (средний и медианный) и feedbacks ───
    top_brands = brand_counts.head(20).index.tolist()
    brand_stats = data_date[data_date['brandName'].isin(top_brands)].groupby('brandName').agg(
        avg_reviewRating=pd.NamedAgg(column='reviewRating', aggfunc='mean'),
        median_reviewRating=pd.NamedAgg(column='reviewRating', aggfunc='median'),
        avg_feedbacks=pd.NamedAgg(column='feedbacks', aggfunc='mean')
    ).sort_values('avg_reviewRating', ascending=False)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
    x = range(len(brand_stats))
    width = 0.35

    # График 1: средний и медианный рейтинг
    ax1.bar([i - width / 2 for i in x], brand_stats['avg_reviewRating'], width=width, label='Средний', alpha=0.8,
            color='steelblue')
    ax1.bar([i + width / 2 for i in x], brand_stats['median_reviewRating'], width=width, label='Медианный', alpha=0.8,
            color='lightblue')
    ax1.set_ylabel('reviewRating')
    ax1.set_xticks(x)
    ax1.set_xticklabels(brand_stats.index, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f"Топ-{len(brand_stats)} брендов: рейтинг", fontsize=11, weight='bold')
    # Рейтинг не может быть выше 5.0
    min_val = min(brand_stats['avg_reviewRating'].min(), brand_stats['median_reviewRating'].min())
    ax1.set_ylim(min_val - 0.2, 5.0)

    # График 2: среднее число отзывов
    ax2.bar(x, brand_stats['avg_feedbacks'], alpha=0.8, color='orange')
    ax2.set_ylabel('Среднее число feedbacks')
    ax2.set_xlabel('Бренд')
    ax2.set_xticks(x)
    ax2.set_xticklabels(brand_stats.index, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    ax2.set_title("Среднее число отзывов", fontsize=11, weight='bold')
    set_smart_ylim(ax2, brand_stats['avg_feedbacks'].values)

    plt.tight_layout()
    save_plot(fig, out_dir / f"5_brand_rating_feedbacks_top{len(brand_stats)}.jpg", False)

    # ─── 6. Топ-20 категорий: reviewRating (средний и медианный) и feedbacks ───
    top_categories = counts.head(20).index.tolist()
    cat_stats = data_date[data_date['entity'].isin(top_categories)].groupby('entity').agg(
        avg_reviewRating=pd.NamedAgg(column='reviewRating', aggfunc='mean'),
        median_reviewRating=pd.NamedAgg(column='reviewRating', aggfunc='median'),
        avg_feedbacks=pd.NamedAgg(column='feedbacks', aggfunc='mean')
    ).sort_values('avg_reviewRating', ascending=False)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
    x = range(len(cat_stats))
    width = 0.35

    # График 1: средний и медианный рейтинг
    ax1.bar([i - width / 2 for i in x], cat_stats['avg_reviewRating'], width=width, label='Средний', alpha=0.8,
            color='green')
    ax1.bar([i + width / 2 for i in x], cat_stats['median_reviewRating'], width=width, label='Медианный', alpha=0.8,
            color='lightgreen')
    ax1.set_ylabel('reviewRating')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cat_stats.index, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f"Топ-{len(cat_stats)} категорий: рейтинг", fontsize=11, weight='bold')
    # Рейтинг не может быть выше 5.0
    min_val = min(cat_stats['avg_reviewRating'].min(), cat_stats['median_reviewRating'].min())
    ax1.set_ylim(min_val - 0.2, 5.0)

    # График 2: среднее число отзывов
    ax2.bar(x, cat_stats['avg_feedbacks'], alpha=0.8, color='purple')
    ax2.set_ylabel('Среднее число feedbacks')
    ax2.set_xlabel('Категория')
    ax2.set_xticks(x)
    ax2.set_xticklabels(cat_stats.index, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    ax2.set_title("Среднее число отзывов", fontsize=11, weight='bold')
    set_smart_ylim(ax2, cat_stats['avg_feedbacks'].values)

    plt.tight_layout()
    save_plot(fig, out_dir / f"6_category_rating_feedbacks_top{len(cat_stats)}.jpg", False)

    # # ─── 7. Топ-10 товаров: по reviewRating ───
    # # Берем только товары с более чем 25 отзывами
    # filtered = data_date[data_date['feedbacks'] > 25]
    # top_by_rating = filtered.nlargest(10, 'reviewRating')[
    #     ['name', 'brandName', 'entity', 'reviewRating', 'feedbacks', 'actualPrice']]
    #
    # if len(top_by_rating) > 0:
    #     fig = plt.figure(figsize=(8, 5))
    #     y_pos = range(len(top_by_rating))
    #     plt.barh(y_pos, top_by_rating['reviewRating'].values, color='gold')
    #     plt.yticks(y_pos, [f"{row['name'][:30]}..." if len(row['name']) > 30 else row['name']
    #                        for _, row in top_by_rating.iterrows()])
    #     plt.xlabel('reviewRating')
    #     plt.title('Топ-10 товаров по рейтингу (>25 отзывов)', fontsize=12, weight='bold')
    #     ax = plt.gca()
    #     # Рейтинг не может быть выше 5.0
    #     min_val = top_by_rating['reviewRating'].min()
    #     ax.set_xlim(min_val - 0.2, 5.0)
    #     plt.gca().invert_yaxis()
    #     plt.tight_layout()
    #     save_plot(fig, out_dir / "7_top10_by_rating.jpg", False)

    # ─── 7. Топ-10 товаров: по feedbacks ───
    top_by_feedbacks = data_date.nlargest(10, 'feedbacks')[
        ['name', 'brandName', 'entity', 'reviewRating', 'feedbacks', 'actualPrice']]

    if len(top_by_feedbacks) > 0:
        fig = plt.figure(figsize=(8, 5))
        y_pos = range(len(top_by_feedbacks))
        plt.barh(y_pos, top_by_feedbacks['feedbacks'].values, color='skyblue')
        plt.yticks(y_pos, [f"{row['name'][:30]}..." if len(row['name']) > 30 else row['name']
                           for _, row in top_by_feedbacks.iterrows()])
        plt.xlabel('feedbacks')
        plt.title('Топ-10 товаров по числу отзывов', fontsize=12, weight='bold')
        ax = plt.gca()
        set_smart_xlim(ax, top_by_feedbacks['feedbacks'].values, margin=0.05)
        plt.gca().invert_yaxis()
        plt.tight_layout()
        save_plot(fig, out_dir / "7_top10_by_feedbacks.jpg", False)


# ══════════════════════════════════════════════════════════════
# АНАЛИТИКА ПО НЕСКОЛЬКИМ ДНЯМ
# ══════════════════════════════════════════════════════════════

def multi_day_analytics(data):
    """Динамика по дням для выбранной категории"""

    data = ensure_str_col(data, 'entity', fill_value='не указан')

    # Подсчитываем количество позиций по каждой категории
    category_counts = data['entity'].value_counts()
    top_20 = category_counts.head(20)

    print("\n📈 Динамика цен и количества товаров по дням для категории")
    print(f"\n🔥 Топ-20 самых популярных категорий (по количеству позиций):\n")

    for i, (category, count) in enumerate(top_20.items(), 1):
        print(f"  {i:2}. {category:<40} ({count:,} позиций)")

    # Получаем список всех доступных категорий для валидации
    uniq_entity = sorted(data['entity'].unique())

    while True:
        entity = input("\nВведите название категории: ").strip().lower()
        if entity in uniq_entity:
            break
        print(f"Категория '{entity}' не найдена. Попробуйте снова.")

    category_data = data[data['entity'] == entity].copy()
    category_data['date'] = pd.to_datetime(category_data['date'])

    daily_stats = category_data.groupby('date').agg(
        avg_price=('actualPrice', 'mean'),
        median_price=('actualPrice', 'median'),
        item_count=('actualPrice', 'count')
    ).sort_index()

    # Три графика
    fig, ax = plt.subplots(3, 1, figsize=(8, 10))
    dates_str = daily_stats.index.astype(str)

    # 1 — Средняя цена
    ax[0].plot(dates_str, daily_stats['avg_price'], marker='o', linewidth=2, color='blue')
    ax[0].set_title(f'Средняя actualPrice по дням — "{entity}"', fontsize=11, weight='bold')
    ax[0].set_ylabel('Средняя цена')
    ax[0].grid(True, alpha=0.3)
    ax[0].tick_params(axis='x', rotation=45)
    set_smart_ylim(ax[0], daily_stats['avg_price'].values)

    # 2 — Медианная цена
    ax[1].plot(dates_str, daily_stats['median_price'], marker='o', linewidth=2, color='green')
    ax[1].set_title('Медианная actualPrice по дням', fontsize=11, weight='bold')
    ax[1].set_ylabel('Медианная цена')
    ax[1].grid(True, alpha=0.3)
    ax[1].tick_params(axis='x', rotation=45)
    set_smart_ylim(ax[1], daily_stats['median_price'].values)

    # 3 — Количество товаров
    ax[2].bar(dates_str, daily_stats['item_count'], color='coral')
    ax[2].set_title('Количество товаров по дням', fontsize=11, weight='bold')
    ax[2].set_xlabel('Дата')
    ax[2].set_ylabel('Товары')
    ax[2].grid(True, alpha=0.3)
    ax[2].tick_params(axis='x', rotation=45)
    set_smart_ylim(ax[2], daily_stats['item_count'].values)

    plt.tight_layout()

    out_dir = USER_REQUEST_OUTPUT
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dates_str[0]}_{dates_str[-1]}_dynamics_{entity}.jpg"

    save_plot(fig, out_path)
    print(f"✓ Динамика для категории '{entity}' сохранена")


# ══════════════════════════════════════════════════════════════
# ГЛАВНАЯ ФУНКЦИЯ
# ══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  АНАЛИТИКА ДАННЫХ WILDBERRIES")
    print("=" * 60)

    conn = get_connection()
    data = load_data(conn)

    if data.empty:
        print("❌ База данных пуста!")
        conn.close()
        return

    # Получаем доступные даты
    available_dates = sorted(data['date'].astype(str).unique())
    print(f"\nДоступно дат в базе: {len(available_dates)}")
    print(f"Диапазон: {available_dates[0]} → {available_dates[-1]}")

    while True:
        print("\n" + "─" * 60)
        print("Выберите тип аналитики:")
        print("  1 — Основная аналитика за ВСЕ дни")
        print("  2 — Динамика по дням для категории (запрос)")
        print("  0 — Выход")
        print("─" * 60)

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("Завершение работы.")
            break


        elif choice == "1":
            print(f"\n🔄 Запуск основной аналики для {len(available_dates)} дат...")

            for date in available_dates:
                basic_analytics_for_date(data, date)

            print("\n✅ Основная аналитика завершена!")

            # ===== НОВОЕ: Объединяем папки в PDF и удаляем их =====

            print("\n📦 Объединяю папки в PDF-файлы...")

            # Обрабатываем каждую папку аналитики за конкретную дату
            analytics_dirs = sorted(BASIC_OUTPUT.glob("*_analytics"))
            for folder in analytics_dirs:
                folder_to_pdf_and_delete(folder)

            print("\n✅ Все PDF-файлы созданы и папки удалены!")

        elif choice == "2":
            multi_day_analytics(data)
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

    conn.close()


if __name__ == "__main__":
    main()
