from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeDriverManager
import pandas as pd
import time

def scrape_jumia(url, num_pages):
    options = Options()
    options.use_chromium = True
    driver = webdriver.Edge(service=Service(EdgeDriverManager().install()), options=options)

    products = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}?page={page}"
        driver.get(page_url)
        time.sleep(2)  # Attendre que la page se charge

        items = driver.find_elements(By.CSS_SELECTOR, ".c4keK")
        for item in items:
            title = item.find_element(By.CSS_SELECTOR, ".name")
            price = item.find_element(By.CSS_SELECTOR, ".price")
            rating = item.find_element(By.CSS_SELECTOR, ".stars")
            product_link = item.find_element(By.CSS_SELECTOR, ".core")

            title_text = title.text.strip() if title else "No Title"
            price_text = price.text.strip() if price else "No Price"
            rating_text = rating.text.strip() if rating else "No Rating"
            product_url = f"https://www.jumia.com.tn{product_link.get_attribute('href')}" if product_link else "No URL"

            if title_text != "No Title":
                product_info = {
                    "Title": title_text,
                    "Price": price_text,
                    "Rating": rating_text,
                    "URL": product_url
                }
                products.append(product_info)
            else:
                print(f"Skipping item with missing title on page {page}")

    driver.quit()
    return products

# Liste des URLs de différentes catégories à scraper sur Jumia
jumia_categories = {
    "Electronics": "https://www.jumia.com.tn/electronique/",
    "Home & Kitchen": "https://www.jumia.com.tn/cuisine-cuisson/",
    "Fashion": "https://www.jumia.com.tn/fashion-mode/"
}

num_pages = 5  # Nombre de pages à scraper

# Dictionnaire pour stocker les données des différentes catégories
category_data = {}

# Scraper les catégories sur Jumia
for category, url in jumia_categories.items():
    print(f"Scraping Jumia category: {category}")
    data = scrape_jumia(url, num_pages)
    category_data[f"Jumia_{category}"] = data

# Enregistrement des résultats dans un fichier Excel avec une feuille par catégorie
with pd.ExcelWriter("jumia_data.xlsx") as writer:
    for category, data in category_data.items():
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=category, index=False)

print("Scraping complete. Data saved to jumia_data.xlsx.")
