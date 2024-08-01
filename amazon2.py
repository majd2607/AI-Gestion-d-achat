import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.preprocessing import MinMaxScaler

nltk.download('vader_lexicon')

def scrape_amazon(url, num_pages, category, provider, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, comme Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"
    }

    products = []

    for page in range(1, num_pages + 1):
        page_url = f"{url}&page={page}"
        for attempt in range(5):
            try:
                response = requests.get(page_url, headers=headers, proxies=proxies)
                if response.status_code == 200:
                    break
                print(f"Failed to retrieve content from page {page}: {response.status_code}, attempt {attempt + 1}")
                time.sleep(random.uniform(30, 60))  # Augmentation du temps d'attente
            except requests.RequestException as e:
                print(f"Request failed: {e}, attempt {attempt + 1}")
                time.sleep(random.uniform(30, 60))  # Augmentation du temps d'attente
        else:
            print(f"Failed to retrieve content from page {page} after 5 attempts.")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        items = soup.select(".s-main-slot .s-result-item")
        if not items:
            print(f"No items found on page {page}")
            continue

        for item in items:
            title = item.select_one("h2 a span")
            price = item.select_one(".a-price > span.a-offscreen")
            rating = item.select_one(".a-icon-alt")
            link = item.select_one("h2 a")["href"] if item.select_one("h2 a") else None

            title_text = title.get_text().strip() if title else "No Title"
            price_text = price.get_text().strip().replace("$", "").replace(",", "") if price else "No Price"
            rating_text = rating.get_text().strip().split()[0] if rating else "No Rating"

            try:
                price_value = float(price_text) if price_text != "No Price" else 0.0
            except ValueError:
                price_value = 0.0

            try:
                rating_value = float(rating_text) if rating_text != "No Rating" else 0.0
            except ValueError:
                rating_value = 0.0

            shipping_text = "No Shipping Info"
            satisfaction_rating = "No Reviews"
            product_url = ""
            if link:
                product_url = "https://www.amazon.com" + link
                shipping_text = scrape_shipping(product_url, headers, proxies)
                satisfaction_rating = analyze_reviews(product_url, headers, proxies)

            brand_text = extract_brand(title_text)

            if title_text != "No Title":
                product_info = {
                    "Category": category,
                    "Title": title_text,
                    "Brand": brand_text,
                    "Price": price_value,
                    "Rating": rating_value,
                    "Shipping": shipping_text,
                    "Comments": satisfaction_rating,
                    "URL": product_url,
                    "Provider": provider
                }
                products.append(product_info)
            else:
                print(f"Skipping item with missing title on page {page}")

        time.sleep(random.uniform(30, 60))  # Augmentation du temps d'attente

    return products

def scrape_shipping(product_url, headers, proxies=None):
    for attempt in range(5):
        try:
            response = requests.get(product_url, headers=headers, proxies=proxies)
            if response.status_code == 200:
                break
            print(f"Failed to retrieve shipping info from product page: {response.status_code}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))  # Augmentation du temps d'attente
        except requests.RequestException as e:
            print(f"Request failed: {e}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))  # Augmentation du temps d'attente
    else:
        return "No Shipping Info"

    soup = BeautifulSoup(response.content, "html.parser")

    shipping_cost = soup.select_one("#exports_desktop_qualifiedBuybox_tlc_feature_div .a-color-secondary")
    if not shipping_cost:
        shipping_cost = soup.select_one("#ddmDeliveryMessage .a-color-base")
    if not shipping_cost:
        shipping_cost = soup.select_one(".a-row.a-spacing-mini .a-size-base")
    if not shipping_cost:
        shipping_cost = soup.select_one("#deliveryMessageMirId .a-color-success")

    return shipping_cost.get_text().strip() if shipping_cost else "No Shipping Info"

def extract_brand(title):
    words = title.split()
    brand = words[0] if words else "No Brand"
    return brand

def analyze_reviews(product_url, headers, proxies=None):
    sia = SentimentIntensityAnalyzer()
    for attempt in range(5):
        try:
            response = requests.get(product_url, headers=headers, proxies=proxies)
            if response.status_code == 200:
                break
            print(f"Failed to retrieve reviews from product page: {response.status_code}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))  # Augmentation du temps d'attente
        except requests.RequestException as e:
            print(f"Request failed: {e}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))  # Augmentation du temps d'attente
    else:
        return "No Reviews"

    soup = BeautifulSoup(response.content, "html.parser")

    reviews = soup.select(".review-text-content span")
    if not reviews:
        return "No Reviews"

    positive_reviews = 0
    total_reviews = 0

    for review in reviews:
        review_text = review.get_text().strip()
        sentiment = sia.polarity_scores(review_text)
        if sentiment["compound"] >= 0.05:
            positive_reviews += 1
        total_reviews += 1

    satisfaction_rating = (positive_reviews / total_reviews) if total_reviews > 0 else "No Reviews"
    return satisfaction_rating

def calculate_global_rating(row, price_weight=0.2, rating_weight=0.4, comment_weight=0.4):
    price_score = 1 - (row["Price"] / df["Price"].max())  # Assuming lower price is better
    rating_score = row["Rating"] / 5.0  # Assuming max rating is 5
    comment_score = row["Comments"]

    global_rating = (price_weight * price_score) + (rating_weight * rating_score) + (comment_weight * comment_score)
    return global_rating

# Liste des URLs de différentes catégories à scraper sur Amazon
amazon_categories = {
    "Smartphones": "https://www.amazon.com/s?k=smartphones&crid=3BXT0JJE3IBFV&sprefix=smartph%2Caps%2C216&ref=nb_sb_ss_pltr-xclick_2_7",
    "Computers & Tablets": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A13896617011&ref=nav_em__nav_desktop_sa_intl_computers_tablets_0_2_6_4",
    "Computer Accessories & Peripherals": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A172456&ref=nav_em__nav_desktop_sa_intl_computer_accessories_and_peripherals_0_2_6_2"
}

num_pages = 5

all_products = []

for category, url in amazon_categories.items():
    print(f"Scraping Amazon category: {category}")
    data = scrape_amazon(url, num_pages, category, "Amazon")
    all_products.extend(data)

df = pd.DataFrame(all_products)

# Normalisation de la colonne Comments pour qu'elle soit entre 0 et 1
df["Comments"] = pd.to_numeric(df["Comments"], errors='coerce').fillna(0)
scaler = MinMaxScaler()
df["Comments"] = scaler.fit_transform(df[["Comments"]])

# Calcul du Global Rating
df["Global Rating"] = df.apply(calculate_global_rating, axis=1)

df = df[["Category", "Title", "Brand", "Price", "Rating", "Shipping", "Comments", "Global Rating", "URL", "Provider"]]

df.to_excel("as.xlsx", index=False)
print("Data saved to amazon_products.xlsx")
