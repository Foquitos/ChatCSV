import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager

# Configurar carpeta de salida
OUTPUT_DIR = "documentacion"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurar opciones de Chrome con soporte para NTLM
USERNAME = "VMAYOMOR"
PASSWORD = "mOuA5847"
DOMAIN = "MERA"  # Cambia esto por el dominio de tu red si es necesario

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

# Configurar la extensión de autenticación automática
auth_plugin_path = "auth_plugin.zip"

def create_auth_extension(username, password):
    """Crear un archivo ZIP que automatice la autenticación NTLM."""
    manifest_json = """
    {
        "manifest_version": 3,
        "name": "Autenticacion NTLM",
        "version": "1.0",
        "permissions": ["webRequest", "webRequestAuthProvider", "webRequestBlocking"],
        "host_permissions": ["<all_urls>"],
        "background": {
            "service_worker": "background.js"
        }
    }
    """
    background_js = f"""
    const config = {{
        username: "{username}",
        password: "{password}"
    }};
    
    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: config.username,
                    password: config.password
                }}
            }};
        }},
        {{ urls: ["<all_urls>"] }},
        ["blocking"]
    );
    """
    with open("manifest.json", "w") as f:
        f.write(manifest_json)
    with open("background.js", "w") as f:
        f.write(background_js)

    # Crear un archivo ZIP con los scripts
    import zipfile
    with zipfile.ZipFile(auth_plugin_path, "w") as z:
        z.write("manifest.json")
        z.write("background.js")

    os.remove("manifest.json")
    os.remove("background.js")



# Crear la extensión
create_auth_extension(f"{USERNAME}", PASSWORD)
chrome_options.add_extension(auth_plugin_path)

# Iniciar el navegador
driver = webdriver.Chrome(options=chrome_options)

# URLs visitadas para evitar duplicados
visited = set()

def scrape_page(url, base_url):
    if url in visited:
        return
    visited.add(url)

    try:
        # Cargar la página con Selenium
        driver.get(url)
        driver.implicitly_wait(10)
        # workspace_element = driver.find_element(By.ID, "scwp-news-table_wrapper")
        soup = BeautifulSoup(driver.page_source, 'html.parser')


        # Obtener el título y crear un archivo de texto
        title = soup.title.string if soup.title else "pagina_sin_titulo"
        file_name = f"{OUTPUT_DIR}/{title.strip().replace('/', '')}.txt"

        # Guardar el contenido de la página en un archivo .txt
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n\n")
            comentario = soup.find(string=lambda text: 'FieldInternalName="Contenido"' in text)
            if comentario:
                # Encuentra el siguiente elemento o contenido después del comentario
                contenido_siguiente = comentario.find_next_sibling()
                
                if contenido_siguiente:
                    f.write( contenido_siguiente.get_text(strip=True))
                else:
                    # Si no hay elemento siguiente, busca en el texto
                    siguiente_texto = comentario.find_next(text=True)
                    f.write( siguiente_texto.strip() if siguiente_texto else None)

        print(f"Guardado: {file_name}")

        # Encontrar todos los enlaces de la página y seguirlos
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if base_url in link:
                scrape_page(link, base_url)
    except Exception as e:
        print(f"Error al procesar {url}: {e}")

if __name__ == "__main__":
    # URL inicial (principal)
    start_url = "https://gps.prismamediosdepago.com/SitePages/Subcategorias.aspx?cid=18"
    base_url = "https://gps.prismamediosdepago.com"

    # Iniciar el scraping
    scrape_page(start_url, base_url)

    # Cerrar el driver de Selenium
    driver.quit()

    # Eliminar el plugin de autenticación
    os.remove(auth_plugin_path)
