import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

def get_aliexpress_products(search_term, num_pages=1):
    products = []
    
    for page in range(1, num_pages + 1):
        headers = {
            'User-Agent': random.choice(user_agents)
        }
        url = f'https://www.aliexpress.com/wholesale?SearchText={search_term}&page={page}'
        
        for attempt in range(3):  # Retry logic
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    break
                else:
                    print(f"Failed to fetch page {page} for search term '{search_term}', status code: {response.status_code}")
                    time.sleep(random.uniform(20, 40))  # Longer delay before retrying
            except Exception as e:
                print(f"Error fetching page {page} for search term '{search_term}': {e}")
                time.sleep(random.uniform(20, 40))  # Longer delay before retrying
        
        if response.status_code != 200:
            print(f"Could not fetch page {page} for search term '{search_term}' after retries.")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: print the HTML to check the structure
        # print(soup.prettify())
        
        items = soup.select('.JIIxO ._3t7zg ._2rkqA a._3t7zg._2f4Ho')

        for item in items:
            title = item.get('title')
            link = item.get('href')
            if title and link:
                products.append({
                    'Title': title,
                    'Link': 'https:' + link
                })
        
        time.sleep(random.uniform(30, 60))  # Longer delay between pages
    
    print(f"Found {len(products)} products for search term '{search_term}'")  # Debugging line
    return products

def scrape_aliexpress_categories(categories, num_pages=1):
    all_data = {}
    for category in categories:
        print(f"Scraping category: {category}")
        products = get_aliexpress_products(category, num_pages)
        all_data[category] = products
        time.sleep(random.uniform(60, 120))  # Longer delay between categories
    
    return all_data

def save_to_excel(data, filename):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        for category, products in data.items():
            df = pd.DataFrame(products)
            print(f"Saving {len(products)} products for category '{category}' to Excel")  # Debugging line
            df.to_excel(writer, sheet_name=category, index=False)

categories = ["electronics", "kitchen", "clothing"]  # Specified categories
num_pages = 1  # Number of pages to scrape
data = scrape_aliexpress_categories(categories, num_pages)
save_to_excel(data, 'aliexpress_products.xlsx')
print("Data saved to aliexpress_products.xlsx")
