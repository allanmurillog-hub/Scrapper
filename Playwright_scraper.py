from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote
import pandas as pd
import time

BASE_URL = "https://clutch.co"
URL = "https://clutch.co/agencies/digital-marketing/california"
MAX_AGENCIAS = 4  # cambia a None o a un número grande si quieres más

datos = []
visitados = set()


def extraer_url_real_desde_redirect(redir_url: str) -> str | None:
    """Extrae y decodifica el parámetro 'u' del redirect de Clutch."""
    if not redir_url:
        return None
    parsed_url = urlparse(redir_url)
    params = parse_qs(parsed_url.query)
    url_real_codificada = params.get("u", [None])[0]
    if not url_real_codificada:
        return None
    return unquote(url_real_codificada)


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
        if MAX_AGENCIAS is not None and len(datos) >= MAX_AGENCIAS:
            break

        # Nombre
        nombre_el = agencia.query_selector("h3")
        if not nombre_el:
            continue
        nombre = nombre_el.inner_text().strip()

        # Perfil URL (idealmente, dentro del bloque de agencia)
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
            perfil_page.wait_for_load_state("domcontentloaded")
            perfil_page.wait_for_timeout(5000)

            # ====== CORRECCIÓN: sacar Visit Website desde EL PERFIL (no desde `page`) ======
            # Si hubiese más de un botón (raro), tomamos el primero que exista.
            web_el = perfil_page.query_selector("a.website-link__item")
            pagina_web = None

            if web_el:
                redir_url = web_el.get_attribute("href")
                pagina_web = extraer_url_real_desde_redirect(redir_url)

            print("Página web real:", pagina_web)

            # Teléfono
            telefono = None
            tel_el = perfil_page.query_selector('a[href^="tel:"]')
            if tel_el:
                telefono = tel_el.get_attribute(
                    "href").replace("tel:", "").strip()

            datos.append({
                "Nombre": nombre,
                "Teléfono": telefono,
                "Perfil": perfil_url
            })

            print(f"✔ {nombre}")
            time.sleep(1)

        except Exception as e:
            print(f"Error al procesar {perfil_url}: {e}")

        finally:
            try:
                perfil_page.close()
            except:
                pass

    browser.close()

# Exportar a Excel
df = pd.DataFrame(datos)
df.to_excel("agencias.xlsx", index=False)

print(f"\n✅ Scraping finalizado. Total agencias: {len(datos)}")
