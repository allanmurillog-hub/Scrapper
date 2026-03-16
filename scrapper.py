from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote
import pandas as pd
import time

BASE_URL = "https://clutch.co"
URL = "https://clutch.co/agencies/digital-marketing/california"
MAX_AGENCIAS = 2

datos = []
visitados = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(URL, timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    # Aceptar cookies si aparece
    try:
        page.click("button:has-text('Accept')", timeout=5000)
    except:
        pass

    # Scroll para cargar contenido
    for _ in range(6):
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(1500)

    agencias = page.query_selector_all("div[class*='provider']")

    print("Agencias detectadas:", len(agencias))

    for agencia in agencias:
        if len(datos) >= MAX_AGENCIAS:
            break

        # Nombre
        nombre_el = agencia.query_selector("h3")
        if not nombre_el:
            continue
        nombre = nombre_el.inner_text().strip()

        # Perfil URL
        perfil_el = agencia.query_selector("a[href]")
        if not perfil_el:
            continue

        perfil_url = perfil_el.get_attribute("href")
        if not perfil_url:
            continue

        if perfil_url.startswith("/"):
            perfil_url = BASE_URL + perfil_url

        if perfil_url in visitados:
            continue
        visitados.add(perfil_url)

        # Abrir perfil
        perfil_page = context.new_page()
        try:
            perfil_page.goto(perfil_url, timeout=60000)
            perfil_page.wait_for_timeout(3000)

            # Página web real
            web_el = page.query_selector("a.website-link__item")
            pagina_web = None

            if web_el:
                redir_url = web_el.get_attribute("href")
                if redir_url:
                    parsed_url = urlparse(redir_url)
                    params = parse_qs(parsed_url.query)
                    url_real_codificada = params.get('u', [None])[0]
                    if url_real_codificada:
                        pagina_web = unquote(url_real_codificada)

            print("Página web real:", pagina_web)

            # Teléfono
            telefono = None
            tel_el = perfil_page.query_selector('a[href^="tel:"]')
            if tel_el:
                telefono = tel_el.get_attribute("href").replace("tel:", "")

            datos.append({
                "Nombre": nombre,
                "Página Web": pagina_web,
                "Teléfono": telefono
            })

            print(f"✔ {nombre}")
            time.sleep(1)

        except Exception as e:
            print(f"Error al procesar {perfil_url}: {e}")

        finally:
            perfil_page.close()

    browser.close()

# Exportar a Excel
df = pd.DataFrame(datos)
df.to_excel("agencias.xlsx", index=False)

print(f"\n✅ Scraping finalizado. Total agencias: {len(datos)}")
