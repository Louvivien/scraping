from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time  
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd

# Voir si ça marche encore en raccourcissant les temps d'attente

def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

def search_contact_info(name, city):
    # Setup Chrome options for headless mode
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')

    # Path to your ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Initialize the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Go to the URL with parameters
    url = f"https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui={name}&ou={city}"
    driver.get(url)

    # Add your code here if you need to interact with the page

    # Wait 
    time.sleep(3) 

    # Try to find and click the "Accepter & Fermer" button if it exists
    try:
        accept_button = driver.find_element(By.XPATH, "//span[text()='Accepter & Fermer']")
        accept_button.click()
        time.sleep(3)  # Wait for any potential pop-up to close
    except NoSuchElementException:
        print("Accepter & Fermer button not found. Continuing...")


    # Wait 
    # time.sleep(60) 
    
    # Find the first h3 element and compare it with the name
    try:
        first_h3_element = driver.find_element(By.TAG_NAME, "h3").text
        print(f"Comparing '{first_h3_element}' with '{name}'")
        if similar(first_h3_element.lower(), name.lower()) < 0.5:
            print("Name doesn't match")
            driver.quit()
            return "Name doesn't match"
        else:
            print("Name match")
    except NoSuchElementException:
        print("No h3 element found. Skipping to next entry...")
        driver.quit()
        return "Name not found"


    # Find and click the "Afficher le N°" button
    show_number_button = driver.find_element(By.XPATH, "//span[@class='value' and contains(text(), 'Afficher le N°')]")
    show_number_button.click()

    # Wait 
    time.sleep(3) 


    # Find the phone number
    phone_number_div = driver.find_element(By.XPATH, "//div[@class='number-contact']/span")
    phone_number = phone_number_div.text

    # Print the phone number or return it from a function
    print(phone_number)


    # Wait for 10 seconds
    # time.sleep(10)  # This will pause the execution for 10 seconds


    # Close the browser
    driver.quit()
    return phone_number


def main(start_row=0):
    # Load Excel file
    file_path = '/Users/vivien/Documents/Scraping/PagesJaunesScraper/Fichier_Prospection_Test.xlsx'
    df = pd.read_excel(file_path)

    # Add a new column for results
    df['Result'] = ''

    # Iterate over the rows of the DataFrame
    for index, row in df.iloc[start_row:].iterrows():
        name = row['Nom / Raison sociale']
        city = row['libelleCommuneEtablissement']
        
        # Call the scraping function
        result = search_contact_info(name, city)
        df.at[index, 'Result'] = result

        # Save partial results every 10 records
        if (index - start_row) % 10 == 9:
            partial_file_path = file_path.replace('.xlsx', f'_partial_{index}.xlsx')
            df.to_excel(partial_file_path, index=False)

    # Save the complete file at the end
    complete_file_path = file_path.replace('.xlsx', '_complete.xlsx')
    df.to_excel(complete_file_path, index=False)

# Example usage, starting from row 20
main(start_row=20)
