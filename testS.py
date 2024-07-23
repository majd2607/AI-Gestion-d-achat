from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
import pandas as pd
import time

# Initialize the driver for Microsoft Edge
driver = webdriver.Edge()

try:
    # Open the AliExpress homepage
    print("Opening AliExpress homepage...")
    driver.get('https://www.aliexpress.com')

    # Wait for the page to load and the search box to be visible
    wait = WebDriverWait(driver, 30)  # Increase wait time to 30 seconds
    search_box = wait.until(EC.visibility_of_element_located((By.NAME, 'SearchText')))
    print("Search box found")

    # Perform a search for a specific product category (e.g., "laptops")
    search_box.send_keys('laptops')
    search_box.submit()
    print("Search initiated")

    # Wait for the search results to load
    time.sleep(5)

    # Find elements that contain the product details
    products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.JIIxO')))
    print(f"Found {len(products)} products")

    # Extract the product details
    product_list = []
    for product in products:
        try:
            name = product.find_element(By.CSS_SELECTOR, 'a._3t7zg').text
            price = product.find_element(By.CSS_SELECTOR, 'span._30jeq3').text
            link = product.find_element(By.CSS_SELECTOR, 'a._3t7zg').get_attribute('href')
            product_list.append([name, price, link])
        except NoSuchElementException as e:
            print(f"Error extracting product details: {e}")
            continue

    # Create a DataFrame with the product details
    df = pd.DataFrame(product_list, columns=['Name', 'Price', 'Link'])

    # Save the product details to an Excel file
    df.to_excel('aliexpress_products.xlsx', index=False)
    print('The product details have been saved to aliexpress_products.xlsx')

except TimeoutException as e:
    print(f"TimeoutException occurred: {e}")
except ElementNotInteractableException as e:
    print(f"ElementNotInteractableException occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    # Close the driver
    driver.quit()
