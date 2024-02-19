import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    options = uc.ChromeOptions()
    # Adjust options as needed
    # options.add_argument('--headless')  # Run in headless mode, remove if you want to see the browser.
    options.add_argument('--disable-gpu')
    driver = uc.Chrome(options=options)
    return driver

def fetch_details(driver, siret):
    try:
        driver.get('https://www.pappers.fr/')
        search_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "q")))
        search_input.clear()
        search_input.send_keys(siret)
        driver.find_element(By.CSS_SELECTOR, 'button:has-text("Rechercher")').click()
        
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.big-text')))
        company_name = driver.find_element(By.CSS_SELECTOR, 'h1.big-text').text
        company_address = driver.find_element(By.CSS_SELECTOR, 'tbody:nth-of-type(1) tr:has(th:has-text("Adresse :")) td').text
        share_capital = "Not Available"  # Initialize as not available in case it's not found.
        
        print(f"SIRET: {siret}, Company Name: {company_name}, Address: {company_address}, Share Capital: {share_capital}")
        return company_name, company_address, share_capital
    except Exception as e:
        print(f"Error fetching details for SIRET {siret}: {e}")
        return "Error", "Error", "Error"

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file, delimiter=';')
    df['Company Name'] = ''
    df['Company Address'] = ''
    df['Share Capital'] = ''
    
    driver = setup_driver()
    
    for index, row in df.iterrows():
        siret = row['siret']
        company_name, company_address, share_capital = fetch_details(driver, str(siret))
        df.at[index, 'Company Name'] = company_name
        df.at[index, 'Company Address'] = company_address
        df.at[index, 'Share Capital'] = share_capital
        
        # Save partial results every 10 entries
        if (index + 1) % 10 == 0:
            partial_filename = output_file.replace('.csv', f'_Partial_{index + 1}.csv')
            df.iloc[:index + 1].to_csv(partial_filename, index=False, sep=';')
            print(f"Saved partial results to {partial_filename}")
    
    driver.quit()
    df.to_csv(output_file, index=False, sep=';')
    print(f"Saved final results to {output_file}")

if __name__ == '__main__':
    input_csv = '/Users/vivien/Documents/Scraping/Pappers/Prosp_Brasseries_PDT.csv'
    output_csv = '/Users/vivien/Documents/Scraping/Pappers/Final_Result.csv'
    process_csv(input_csv, output_csv)
