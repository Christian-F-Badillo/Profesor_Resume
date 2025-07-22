import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from pathlib import Path
import re

# Paths seguros
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

URL_UNIVERSITY = "https://www.misprofesores.com/escuelas/Facultad-de-Psicologia-UNAM_1805"
TABLE_NAME_PATH = DATA_DIR / "tabla_profesores.csv"
LINKS_NAME_PATH = DATA_DIR / "enlaces_profesores.csv"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL_UNIVERSITY)
        
        await page.wait_for_selector("tr")
        print("Página cargada:", await page.title())

        # Obtener filas
        raw_rows = await page.locator("tr").all_inner_texts()
        tabla = [row.split("\t") for row in raw_rows if row.strip()]

        # Enlaces
        link_locators = page.locator("td.url.hidden-xs.sorting_1 a")
        n = await link_locators.count()
        hrefs = [await link_locators.nth(i).get_attribute("href") for i in range(n)]

        # Guardar
        datos = []

        for row in tabla:
            row = [cell.strip() for cell in row if cell.strip()]

            if len(row) < 3:
                continue  # no tiene lo esencial

            nombre = row[0]
            dep = row[1] if len(row) == 4 else None

            review_str = row[-2]  # penúltimo campo
            rating_str = row[-1]  # último campo

            # Validamos número de reviews
            match_reviews = re.match(r"(\d+)", review_str)
            try:
                num_reviews = int(match_reviews.group()) if match_reviews else None
                rating = float(rating_str)
            except:
                continue  # si falla conversión, lo ignoramos

            if nombre and num_reviews is not None and rating is not None:
                datos.append({
                    "profesor": nombre,
                    "dep": dep,
                    "num_reviews": num_reviews,
                    "rating": rating
                })

        # Convertir a DataFrame
        df = pd.DataFrame(datos)
        df.to_csv(TABLE_NAME_PATH, index=False)
        print(f"Tabla guardada en {TABLE_NAME_PATH}")
        # Guardar enlaces
        enlaces_df = pd.DataFrame({"enlace": hrefs})
        enlaces_df.to_csv(LINKS_NAME_PATH, index=False)
        print(f"Enlaces guardados en {LINKS_NAME_PATH}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
