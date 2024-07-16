import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_amazon(url, num_pages):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"  # Do Not Track Request Header
    }

    products = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}&page={page}"
        response = requests.get(page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve content from page {page}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        for item in soup.select(".s-main-slot .s-result-item"):
            title = item.select_one("h2 a span")
            price = item.select_one(".a-price > span.a-offscreen")
            rating = item.select_one(".a-icon-alt")

            title_text = title.get_text().strip() if title else "No Title"
            price_text = price.get_text().strip() if price else "No Price"
            rating_text = rating.get_text().strip() if rating else "No Rating"

            if title_text != "No Title":
                product_info = {
                    "Title": title_text,
                    "Price": price_text,
                    "Rating": rating_text
                }
                products.append(product_info)
            else:
                print(f"Skipping item with missing title on page {page}")

    return products

def scrape_ebay(url, num_pages):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"  # Do Not Track Request Header
    }

    products = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}&_pgn={page}"
        response = requests.get(page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve content from page {page}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        for item in soup.select(".s-item"):
            title = item.select_one(".s-item__title")
            price = item.select_one(".s-item__price")
            rating = item.select_one(".s-item__reviews .clipped")
            rating_alt = item.select_one(".b-starrating__star .clipped")

            title_text = title.get_text().strip() if title else "No Title"
            price_text = price.get_text().strip() if price else "No Price"
            rating_text = rating.get_text().strip() if rating else (rating_alt.get_text().strip() if rating_alt else "No Rating")

            if title_text != "No Title":
                product_info = {
                    "Title": title_text,
                    "Price": price_text,
                    "Rating": rating_text
                }
                products.append(product_info)
            else:
                print(f"Skipping item with missing title on page {page}")

    return products

def scrape_aliexpress(url, num_pages):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"  # Do Not Track Request Header
    }

    products = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}&page={page}"
        response = requests.get(page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve content from page {page}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        for item in soup.select(".list-item"):
            title = item.select_one(".item-title")
            price = item.select_one(".price-current")
            rating = item.select_one(".rating-value")

            title_text = title.get_text().strip() if title else "No Title"
            price_text = price.get_text().strip() if price else "No Price"
            rating_text = rating.get_text().strip() if rating else "No Rating"

            if title_text != "No Title":
                product_info = {
                    "Title": title_text,
                    "Price": price_text,
                    "Rating": rating_text
                }
                products.append(product_info)
            else:
                print(f"Skipping item with missing title on page {page}")

    return products

# Liste des URLs de différentes catégories à scraper sur Amazon
amazon_categories = {
    "Electronics": "https://www.amazon.com/s?k=electronics",
    "Home & Kitchen": "https://www.amazon.com/s?k=home+and+kitchen",
    "Clothing": "https://www.amazon.com/s?k=clothing"
}

# Liste des URLs de différentes catégories à scraper sur eBay
ebay_categories = {
    "Electronics": "https://www.ebay.com/sch/i.html?_nkw=electronics",
    "Home & Kitchen": "https://www.ebay.com/sch/i.html?_nkw=home+and+kitchen",
    "Clothing": "https://www.ebay.com/sch/i.html?_nkw=clothing"
}

# Liste des URLs de différentes catégories à scraper sur AliExpress
aliexpress_categories = {
    "Electronics": "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20210716034236&SearchText=electronics",
    "Home & Kitchen": "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20210716034236&SearchText=home+and+kitchen",
    "Clothing": "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20210716034236&SearchText=clothing"
}

num_pages = 5  # Nombre de pages à scraper

# Dictionnaire pour stocker les données des différentes catégories
category_data = {}

# Scraper les catégories sur Amazon
for category, url in amazon_categories.items():
    print(f"Scraping Amazon category: {category}")
    data = scrape_amazon(url, num_pages)
    category_data[f"Amazon_{category}"] = data

# Scraper les catégories sur eBay
for category, url in ebay_categories.items():
    print(f"Scraping eBay category: {category}")
    data = scrape_ebay(url, num_pages)
    category_data[f"eBay_{category}"] = data

# Scraper les catégories sur AliExpress
for category, url in aliexpress_categories.items():
    print(f"Scraping AliExpress category: {category}")
    data = scrape_aliexpress(url, num_pages)
    category_data[f"AliExpress_{category}"] = data

# Enregistrement des résultats dans un fichier Excel avec une feuille par catégorie
with pd.ExcelWriter("amazon_ebay_aliexpress_products55.xlsx") as writer:
    for category, data in category_data.items():
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=category, index=False)

print("Scraping complete. Data saved to amazon_ebay_aliexpress_products.xlsx.")
