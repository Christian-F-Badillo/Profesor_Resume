import pandas as pd
import os
from pathlib import Path

# Paths seguros
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

TAGS_DIR = DATA_DIR / "tags_individuales"
REVIEWS_DIR = DATA_DIR / "reviews_individuales"
TAGS_DIR.mkdir(exist_ok=True)
REVIEWS_DIR.mkdir(exist_ok=True)

def merge_data():
    # Cargar los archivos CSV de tags y reviews
    tags_files = list(TAGS_DIR.glob("*.csv"))
    reviews_files = list(REVIEWS_DIR.glob("*.csv"))

    if not tags_files or not reviews_files:
        print("No se encontraron archivos de tags o reviews para fusionar.")
        return

    # Leer y concatenar los DataFrames de tags
    tags_dfs = [pd.read_csv(file) for file in tags_files]
    merged_tags = pd.concat(tags_dfs, ignore_index=True)

    # Leer y concatenar los DataFrames de reviews
    reviews_dfs = [pd.read_csv(file) for file in reviews_files]
    merged_reviews = pd.concat(reviews_dfs, ignore_index=True)

    # Guardar los DataFrames fusionados
    merged_tags.to_csv(DATA_DIR / "merged_tags.csv", index=False)
    merged_reviews.to_csv(DATA_DIR / "merged_reviews.csv", index=False)

    print("Datos fusionados y guardados correctamente.")

if __name__ == "__main__":
    merge_data()
    print("Proceso de fusión de datos completado.")
