import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def scrape_phone_number(address):

    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')
    chrome_options.page_load_strategy = 'normal'  # Change page load strategy

    # Path to your ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Initialize the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.google.com/maps")
    print("Navigated to Google Maps successfully.")

    # Handle cookie acceptance
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label, "Accept")]'))
        )
        accept_button.click()
        print("Accepted cookies.")
    except Exception as e:
        print("No cookie acceptance button found or other error.")

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'searchboxinput'))
    )
    search_box.send_keys(address)
    search_box.send_keys(Keys.ENTER)
    print("Business search initiated.")

    # Add logic here to wait for search results and interact with them

    # Extract phone number
    try:
        phone_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.CsEnBe[data-item-id*="phone"]'))
        )
        phone_number = phone_button.get_attribute('aria-label').replace('Phone: ', '')
    except Exception as e:
        phone_number = 'Phone number not found'
        print(f"Error finding phone number: {e}")

    print(f'Phone Number: {phone_number}')

    driver.quit()
    return phone_number


def main(start_row=0):
    df = pd.read_csv('/Users/vivien/Documents/Scraping/GmapScraper/brasseries.csv')
    df.fillna('', inplace=True)
    df = df[df['denominationUniteLegale'].notna() & df['denominationUniteLegale'].ne('')]

    print(f"Starting from row: {start_row}")
    print(f"Number of rows in DataFrame after filtering: {len(df)}")

    df['phone_number'] = ''

    # Define the filename for the partial save
    partial_save_filename = '/Users/vivien/Documents/Scraping/GmapScraper/brasseries_with_phones_partial.csv'

    for index, row in df[start_row:].iterrows():
        address = f"{row['denominationUniteLegale']} {row['complementAdresseEtablissement']} {row['numeroVoieEtablissement']} {row['indiceRepetitionEtablissement']} {row['typeVoieEtablissement']} {row['libelleVoieEtablissement']} {row['codePostalEtablissement']} {row['libelleCommuneEtablissement']}"
        try:
            phone_number = scrape_phone_number(address)
        except Exception as e:
            print(f"Error occurred while processing address: {address}. Error: {e}")
            phone_number = 'Error'
        df.at[index, 'phone_number'] = phone_number

        # Every 10 rows, append the processed rows to the partial CSV
        if (index - start_row + 1) % 10 == 0:
            with open(partial_save_filename, 'a') as f:
                df[start_row:index+1].to_csv(f, header=f.tell()==0, index=False)
            print(f"Saved progress up to row {index+1}")

        print(f"Processed row {index+1}/{len(df)}")

    # Save the final DataFrame
    df.to_csv('/Users/vivien/Documents/Scraping/GmapScraper/brasseries_with_phones.csv', index=False)

start_row_number = 0  # Modify this to start from a different row
main(start_row=start_row_number)