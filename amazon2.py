import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.preprocessing import MinMaxScaler

nltk.download('vader_lexicon')

def scrape_amazon(url, category, provider, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"
    }

    products = []
    page = 1

    while len(products) < 10:
        page_url = f"{url}&page={page}"
        for attempt in range(5):
            try:
                response = requests.get(page_url, headers=headers, proxies=proxies)
                if response.status_code == 200:
                    break
                print(f"Failed to retrieve content from page {page}: {response.status_code}, attempt {attempt + 1}")
                time.sleep(random.uniform(30, 60))
            except requests.RequestException as e:
                print(f"Request failed: {e}, attempt {attempt + 1}")
                time.sleep(random.uniform(30, 60))
        else:
            print(f"Failed to retrieve content from page {page} after 5 attempts.")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.select(".s-main-slot .s-result-item")
        if not items:
            print(f"No items found on page {page}")
            break

        for item in items:
            title = item.select_one("h2 a span")
            price = item.select_one(".a-price > span.a-offscreen")
            rating = item.select_one(".a-icon-alt")
            link = item.select_one("h2 a")["href"] if item.select_one("h2 a") else None
            image = item.select_one(".s-image")["src"] if item.select_one(".s-image") else None

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
                    "Image": image,
                    "Comments": satisfaction_rating,
                    "URL": product_url,
                    "Provider": provider
                }
                products.append(product_info)
            if len(products) >= 10:
                break

        page += 1
        time.sleep(random.uniform(30, 60))

    return products

def scrape_shipping(product_url, headers, proxies=None):
    for attempt in range(5):
        try:
            response = requests.get(product_url, headers=headers, proxies=proxies)
            if response.status_code == 200:
                break
            print(f"Failed to retrieve shipping info from product page: {response.status_code}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))
        except requests.RequestException as e:
            print(f"Request failed: {e}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))
    else:
        return "No Shipping Info"

    soup = BeautifulSoup(response.content, "html.parser")
    shipping_cost = soup.select_one("span.a-size-base.a-color-secondary")
    if shipping_cost:
        shipping_text = shipping_cost.get_text().strip()
        if "$" in shipping_text:
            return shipping_text.split('$')[-1].split()[0].replace(",", "")
    return "No Shipping Info"

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
            time.sleep(random.uniform(10, 20))
        except requests.RequestException as e:
            print(f"Request failed: {e}, attempt {attempt + 1}")
            time.sleep(random.uniform(10, 20))
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

def calculate_global_rating(row, price_weight=0.2, rating_weight=0.3, comment_weight=0.3, shipping_weight=0.2):
    price_score = 1 - (row["Price"] / df["Price"].max())
    rating_score = row["Rating"] / 5.0
    comment_score = row["Comments"]
    try:
        shipping_cost = float(row["Shipping"])
    except ValueError:
        shipping_cost = 0.0
    shipping_score = 1 - (shipping_cost / df["Shipping"].apply(lambda x: float(x) if x != "No Shipping Info" else 0.0).max())

    global_rating = (price_weight * price_score) + (rating_weight * rating_score) + (comment_weight * comment_score) + (shipping_weight * shipping_score)
    return global_rating

amazon_categories = {
    "Smartphones": "https://www.amazon.com/s?k=smartphones&crid=3BXT0JJE3IBFV&sprefix=smartph%2Caps%2C216&ref=nb_sb_ss_pltr-xclick_2_7",
    "Computers & Tablets": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A13896617011&ref=nav_em__nav_desktop_sa_intl_computers_tablets_0_2_6_4",
    "Computer Accessories & Peripherals": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A172456&ref=nav_em__nav_desktop_sa_intl_computer_accessories_and_peripherals_0_2_6_2"
}

all_products = []

for category, url in amazon_categories.items():
    print(f"Scraping Amazon category: {category}")
    data = scrape_amazon(url, category, "Amazon")
    all_products.extend(data)

df = pd.DataFrame(all_products)

df["Comments"] = pd.to_numeric(df["Comments"], errors='coerce').fillna(0)
scaler = MinMaxScaler()
df["Comments"] = scaler.fit_transform(df[["Comments"]])

df["Global Rating"] = df.apply(calculate_global_rating, axis=1)

df = df[["Category", "Title", "Brand", "Price", "Rating", "Shipping", "Image", "Comments", "Global Rating", "URL", "Provider"]]

df.to_excel("aaucts.xlsx", index=False)
print("Data saved to amazon_products.xlsx")
