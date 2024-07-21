from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Initialize the driver for Microsoft Edge
driver = webdriver.Edge()

# Open the Amazon homepage
driver.get('https://www.amazon.com')

# Wait for the user to solve the CAPTCHA (if necessary)
input("Resolve the CAPTCHA manually, then press Enter to continue...")

# Wait a bit to ensure the page is fully loaded
time.sleep(5)

# Open the category menu
menu_button = driver.find_element(By.ID, 'nav-hamburger-menu')
menu_button.click()

# Wait for the menu to load
time.sleep(2)

# Find elements that contain the product categories
categories = driver.find_elements(By.CSS_SELECTOR, 'ul.hmenu-visible li a.hmenu-item')

# Extract the names of the categories
category_names = [category.text for category in categories if category.text]

# Close the driver
driver.quit()

# Create a DataFrame with the names of the categories
df = pd.DataFrame(category_names, columns=['Category'])

# Save the categories to an Excel file
df.to_excel('amazon_product_categories.xlsx', index=False)

print('The product categories have been saved to amazon_product_categories.xlsx')
