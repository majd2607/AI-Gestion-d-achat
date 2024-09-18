import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def scrape_amazon(url, num_pages, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"
    }

    products = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}&page={page}"
        for attempt in range(5):  # Tenter jusqu'à 5 fois
            try:
                response = requests.get(page_url, headers=headers, proxies=proxies)
                if response.status_code == 200:
                    break
                print(f"Failed to retrieve content from page {page}: {response.status_code}, attempt {attempt + 1}")
                time.sleep(random.uniform(5, 10))  # Attendre entre 5 et 10 secondes avant de réessayer
            except requests.RequestException as e:
                print(f"Request failed: {e}, attempt {attempt + 1}")
                time.sleep(random.uniform(5, 10))  # Attendre entre 5 et 10 secondes avant de réessayer
        else:
            print(f"Failed to retrieve content from page {page} after 5 attempts.")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        for item in soup.select(".s-main-slot .s-result-item"):
            title = item.select_one("h2 a span")
            price = item.select_one(".a-price > span.a-offscreen")
            rating = item.select_one(".a-icon-alt")
            link = item.select_one("h2 a")["href"] if item.select_one("h2 a") else None

            title_text = title.get_text().strip() if title else "No Title"
            price_text = price.get_text().strip() if price else "No Price"
            rating_text = rating.get_text().strip() if rating else "No Rating"

            comment_text = "No Comment"
            if link:
                product_url = "https://www.amazon.com" + link
                comment_text = scrape_comment(product_url, headers, proxies)

            if title_text != "No Title":
                product_info = {
                    "Title": title_text,
                    "Price": price_text,
                    "Rating": rating_text,
                    "Comment": comment_text
                }
                products.append(product_info)
            else:
                print(f"Skipping item with missing title on page {page}")

        # Ajouter un délai entre les pages pour éviter d'être bloqué
        time.sleep(random.uniform(10, 20))

    return products

def scrape_comment(product_url, headers, proxies=None):
    for attempt in range(5):  # Tenter jusqu'à 5 fois
        try:
            response = requests.get(product_url, headers=headers, proxies=proxies)
            if response.status_code == 200:
                break
            print(f"Failed to retrieve comments from product page: {response.status_code}, attempt {attempt + 1}")
            time.sleep(random.uniform(5, 10))  # Attendre entre 5 et 10 secondes avant de réessayer
        except requests.RequestException as e:
            print(f"Request failed: {e}, attempt {attempt + 1}")
            time.sleep(random.uniform(5, 10))  # Attendre entre 5 et 10 secondes avant de réessayer
    else:
        return "No Comment"

    soup = BeautifulSoup(response.content, "html.parser")
    comment = soup.select_one(".review-text-content span")
    return comment.get_text().strip() if comment else "No Comment"

# Liste des URLs de différentes catégories à scraper sur Amazon
amazon_categories = {
    "Electronics": "https://www.amazon.com/s?k=electronics",
    "Home & Kitchen": "https://www.amazon.com/s?k=home+and+kitchen",
    "Clothing": "https://www.amazon.com/s?k=clothing"
}

num_pages = 5  # Nombre de pages à scraper

# Dictionnaire pour stocker les données des différentes catégories
category_data = {}

# Scraper les catégories sur Amazon
for category, url in amazon_categories.items():
    print(f"Scraping Amazon category: {category}")
    data = scrape_amazon(url, num_pages)
    category_data[f"Amazon_{category}"] = data

# Enregistrement des résultats dans un fichier Excel avec une feuille par catégorie
with pd.ExcelWriter("amazon_products_with_comments.xlsx") as writer:
    for category, data in category_data.items():
        if data:  # Vérifier s'il y a des données avant de les enregistrer
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=category, index=False)
        else:
            print(f"No data found for category: {category}")

print("Scraping complete. Data saved to amazon_products_with_comments.xlsx.")
