"""
Скрипт достает все значения категорий из .csv файла.
"""

import pandas as pd
from pathlib import Path

def show_categories(csv_file):
    """
    Категории
    """
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    file_path = PROJECT_ROOT / "data" / "raw_data" / csv_file

    df = pd.read_csv(file_path)
    categories = sorted(df['entity'].dropna().unique())

    print(f"\nКАТЕГОРИИ ИЗ {csv_file}:")
    for i, cat in enumerate(categories, 1):
        print(f"{i:3d}. {cat}")
    print(f"Всего: {len(categories)} категорий")


# Укажите нужный файл
show_categories("2025-11-14_data.csv")