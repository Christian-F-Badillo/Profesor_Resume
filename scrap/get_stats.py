import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from pathlib import Path
import re
from hashlib import md5
import unicodedata

# Paths seguros
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

TAGS_DIR = DATA_DIR / "tags_individuales"
REVIEWS_DIR = DATA_DIR / "reviews_individuales"
TAGS_DIR.mkdir(exist_ok=True)
REVIEWS_DIR.mkdir(exist_ok=True)

data = pd.read_csv(DATA_DIR / "merged_profesores.csv")
urls = data["enlace"].tolist()
profesores = data["profesor"].tolist()

# Función para convertir nombre a nombre de archivo seguro
def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        print("Navegador iniciado")
        print(f"Total de URLs a procesar: {len(urls)}")

        for i, url in enumerate(urls):
            nombre_profesor = profesores[i]
            print(f"\nExtrayendo datos del profesor {i + 1}/{len(urls)}: {nombre_profesor}")

            if pd.isna(url) or url.strip() == "":
                print(f"URL vacía para el profesor {nombre_profesor}, saltando...")
                continue

            page = await browser.new_page()
            await page.goto(url)
            print("Página cargada:", await page.title())

            all_tags = []
            all_comments = []
            all_dates = []
            all_stats = []

            page_num = 1
            last_page_hash = None
            sin_cambio = 0
            max_paginas_sin_cambio = 3

            while True:
                print(f"\nExtrayendo página {page_num}...")

                try:
                    await page.wait_for_selector("div.date", timeout=100000)
                    await page.wait_for_timeout(9000)
                except:
                    print("⚠️ Timeout esperando 'div.date'. Rompiendo el ciclo.")
                    break

                current_html = await page.content()
                current_hash = md5(current_html.encode()).hexdigest()

                if current_hash == last_page_hash:
                    sin_cambio += 1
                    print(f"⚠️ Página no cambió ({sin_cambio}/{max_paginas_sin_cambio})")
                    if sin_cambio >= max_paginas_sin_cambio:
                        print("⛔ Contenido repetido. Asumiendo fin de paginación.")
                        break
                else:
                    sin_cambio = 0

                last_page_hash = current_hash

                # Extraer información
                tags = await page.locator("div.tagbox span").all_inner_texts()
                comments = await page.locator("p.commentsParagraph").all_inner_texts()
                date_comment = await page.locator("div.date").all_inner_texts()
                stats = await page.locator('div.descriptor-container').all_inner_texts()

                all_tags.extend(tags)
                all_comments.extend(comments)
                all_dates.extend(date_comment)
                all_stats.extend(stats)

                # Intentar encontrar el botón "Siguiente"
                try:
                    pagination_lis = page.locator("ul.pagination li")
                    last_li = pagination_lis.nth(await pagination_lis.count() - 1)
                    last_li_class = await last_li.get_attribute("class")

                    if last_li_class and "disabled" in last_li_class:
                        print("✅ Última página alcanzada.")
                        break

                    await last_li.locator("a").click(force=True)
                    print("➡️ Click en siguiente")
                    await page.wait_for_timeout(30000)
                except Exception as e:
                    print("❌ No se pudo hacer clic en siguiente:", str(e))
                    break

                page_num += 1

            print("\nResumen:")
            print("  Total de comentarios extraídos:", len(all_comments))
            print("  Total de etiquetas extraídas:", len(all_tags))

            tags_str = ', '.join(list(set(all_tags)))
            stats_tuples = [s.split("\n") for s in all_stats]

            clean_stats = {
                "calidad_general": [],
                "facilidad": []
            }

            # Validación: asegurar que haya número par de elementos
            if len(stats_tuples) % 2 != 0:
                raise ValueError("Número impar de entradas en stats_tuples; deberían ser pares de calidad y facilidad.")

            # Procesar de dos en dos
            for i in range(0, len(stats_tuples), 2):
                calidad = stats_tuples[i]
                facilidad = stats_tuples[i + 1]

                if "CALIDAD" in calidad[1].upper() and "FACILIDAD" in facilidad[1].upper():
                    clean_stats["calidad_general"].append(calidad[0].strip())
                    clean_stats["facilidad"].append(facilidad[0].strip())
                else:
                    # Si están invertidos o mal ordenados
                    print(f"⚠️ Orden inesperado en el par {calidad}, {facilidad}. Asignando de forma segura.")
                    val1, lab1 = calidad[0].strip(), calidad[1].strip().upper()
                    val2, lab2 = facilidad[0].strip(), facilidad[1].strip().upper()

                    if "CALIDAD" in lab1:
                        clean_stats["calidad_general"].append(val1)
                        clean_stats["facilidad"].append(val2)
                    elif "CALIDAD" in lab2:
                        clean_stats["calidad_general"].append(val2)
                        clean_stats["facilidad"].append(val1)
                    else:
                        # No se identifican correctamente, poner vacíos
                        clean_stats["calidad_general"].append("")
                        clean_stats["facilidad"].append("")

            # Guardar tags individuales
            tags_df = pd.DataFrame({
                "profesor": [nombre_profesor],
                "tags": [tags_str]
            })
            tags_filename = TAGS_DIR / f"{slugify(nombre_profesor)}_tags.csv"
            tags_df.to_csv(tags_filename, index=False)
            print(f"✅ Tags guardados en {tags_filename.name}")

            # Guardar reseñas individuales
            # Asegurar que todas las listas tengan la misma longitud
            n = min(len(all_comments), len(all_dates), len(clean_stats["calidad_general"]), len(clean_stats["facilidad"]))

            if n == 0:
                print(f"⚠️ No hay datos suficientes para guardar reseñas para {nombre_profesor}.")
            else:
                reviews_df = pd.DataFrame({
                    "profesor": [nombre_profesor] * n,
                    "fecha": all_dates[:n],
                    "comentario": all_comments[:n],
                    "calidad_general": clean_stats["calidad_general"][:n],
                    "facilidad": clean_stats["facilidad"][:n]
                })

                reviews_filename = REVIEWS_DIR / f"{slugify(nombre_profesor)}_reviews.csv"
                reviews_df.to_csv(reviews_filename, index=False)
                print(f"✅ Reseñas guardadas en {reviews_filename.name}")

            await page.close()

        await browser.close()
        print("\n✅ Navegador cerrado y extracción finalizada.")
        print(f"Archivos individuales guardados en:\n - {TAGS_DIR}\n - {REVIEWS_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
