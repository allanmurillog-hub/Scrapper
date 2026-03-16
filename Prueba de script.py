from playwright.sync_api import sync_playwright

# URL de ejemplo de un perfil de agencia en clutch.co (cámbiala por una real)
perfil_url = ""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(perfil_url, timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    try:
        # Esperar y buscar el enlace a la página web real
        web_el = page.wait_for_selector("a.website-link__item", timeout=10000)
        href = web_el.get_attribute("href")
        if href:
            print("Página web encontrada:", href)
        else:
            print("No se encontró href en el enlace.")
    except:
        print("No se encontró el enlace con la clase 'website-link__item'.")

    browser.close()
