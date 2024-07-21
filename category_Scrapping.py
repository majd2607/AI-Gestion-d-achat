from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Initialiser le driver pour Microsoft Edge
driver = webdriver.Edge()

# Ouvrir la page d'accueil d'Amazon
driver.get('https://www.amazon.com')

# Attendre que l'utilisateur résolve le CAPTCHA (si nécessaire)
input("Résolvez le CAPTCHA manuellement, puis appuyez sur Entrée pour continuer...")

# Attendre un peu pour s'assurer que la page est complètement chargée
time.sleep(5)

# Trouver les éléments qui contiennent les catégories dans la barre de navigation
categories = driver.find_elements(By.CSS_SELECTOR, 'div#nav-main a.nav-a')

# Extraire les noms des catégories
category_names = [category.text for category in categories if category.text]

# Fermer le driver
driver.quit()

# Créer un DataFrame avec les noms des catégories
df = pd.DataFrame(category_names, columns=['Category'])

# Sauvegarder les catégories dans un fichier Excel
df.to_excel('amazon_categories.xlsx', index=False)

print('Les catégories ont été sauvegardées dans le fichier amazon_categories.xlsx')
