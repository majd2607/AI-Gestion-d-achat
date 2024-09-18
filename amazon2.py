import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

def scrape_amazon(url, category, provider, proxies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1"
    }

    products = []
    page = 1

    while len(products) < 10:
        page_url = f"{url}&page={page}"
        print(f"Scraping page: {page_url}")

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
            break

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

            shipping_text = 0.0
            satisfaction_rating = 0.0
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
        return 0.0

    soup = BeautifulSoup(response.content, "html.parser")
    shipping_cost = soup.select_one(".a-size-base.a-color-secondary")
    
    if shipping_cost:
        shipping_text = shipping_cost.get_text().strip()
        try:
            if "$" in shipping_text:
                cost_text = shipping_text.split('$')[-1].split()[0]
                cost_text = ''.join(c for c in cost_text if c.isdigit() or c == '.')
                return float(cost_text) if cost_text else 0.0
        except ValueError:
            return 0.0
    return 0.0

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
        return 0.0

    soup = BeautifulSoup(response.content, "html.parser")
    reviews = soup.select(".review-text-content span")
    if not reviews:
        return 0.0

    positive_reviews = 0
    total_reviews = 0

    for review in reviews:
        review_text = review.get_text().strip()
        sentiment = sia.polarity_scores(review_text)
        if sentiment["compound"] >= 0.05:
            positive_reviews += 1
        total_reviews += 1

    satisfaction_rating = (positive_reviews / total_reviews) if total_reviews > 0 else 0.0
    return satisfaction_rating

def calculate_global_rating(row, price_weight=0.2, rating_weight=0.3, comment_weight=0.3, shipping_weight=0.2):
    price_score = 1 - (row["Price"] / df["Price"].max())
    rating_score = row["Rating"] / 5.0
    comment_score = row["Comments"]
    shipping_score = 1 - (row["Shipping"] / df["Shipping"].max()) if df["Shipping"].max() != 0 else 0.0

    global_rating = (price_weight * price_score) + (rating_weight * rating_score) + (comment_weight * comment_score) + (shipping_weight * shipping_score)
    return global_rating

def save_to_excel(df, filename="test.xlsx"):
    df.to_excel(filename, index=False)

amazon_categories = {
    "Car & Vehicle Electronics": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A3248684011&ref=nav_em__nav_desktop_sa_intl_car_and_vehicle_electronics_0_2_5_4",
    "Cell Phones & Accessories": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A2811119011&ref=nav_em__nav_desktop_sa_intl_cell_phones_and_accessories_0_2_5_5",
    "Television & Video": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A1266092011&ref=nav_em__nav_desktop_sa_intl_television_and_video_0_2_5_14",
    "Computers & Tablets": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A13896617011&ref=nav_em__nav_desktop_sa_intl_computers_tablets_0_2_6_4",
    "Laptop Accessories": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A3011391011&ref=nav_em__nav_desktop_sa_intl_laptop_accessories_0_2_6_7",
    "Computer Components": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A193870011&ref=nav_em__nav_desktop_sa_intl_computer_components_0_2_6_8",
    "Computer Accessories & Peripherals": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A172456&ref=nav_em__nav_desktop_sa_intl_computer_accessories_0_2_6_5",
    "Computer Networking": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A172504&ref=nav_em__nav_desktop_sa_intl_computer_networking_0_2_6_9",
    "Tablet Accessories": "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A17697096011&ref=nav_em__nav_desktop_sa_intl_tablet_accessories_0_2_6_15",
    "Car Electronics & Accessories": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A706814011&ref=nav_em__nav_desktop_sa_intl_car_electronics_and_accessories_0_2_5_5",
    "Automotive Exterior Accessories": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A15718271&ref=nav_em__nav_desktop_sa_intl_automotive_exterior_accessories_0_2_5_6",
    "Interior Accessories": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A15737351&ref=nav_em__nav_desktop_sa_intl_interior_accessories_0_2_5_7",
    "Car Care": "https://www.amazon.com/s?i=specialty-aps&bbn=16225009011&rh=n%3A%2116225009011%2Cn%3A15718291&ref=nav_em__nav_desktop_sa_intl_car_care_0_2_5_8"
}

# Combined data from all categories
all_products = []

for category, url in amazon_categories.items():
    products = scrape_amazon(url, category, "Amazon")
    all_products.extend(products)

df = pd.DataFrame(all_products)

df["Global Rating"] = df.apply(calculate_global_rating, axis=1)

# Add Id column
df.insert(0, 'Id', range(1, len(df) + 1))

# Move Global Rating column to the desired position
cols = df.columns.tolist()
global_rating_index = cols.index('Global Rating')
comments_index = cols.index('Comments')

# Remove 'Global Rating' from its current position
cols.pop(global_rating_index)
# Insert 'Global Rating' after 'Comments'
cols.insert(comments_index + 1, 'Global Rating')

df = df[cols]

save_to_excel(df)

print("Scraping and saving to Excel completed.")
