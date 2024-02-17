from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time  
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

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
    time.sleep(5) 

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
        print(f"Comparing '{first_h3_element}' with '{name}'")  # Display what is being compared
        if similar(first_h3_element.lower(), name.lower()) < 0.5:
            print("Name doesn't match")
            driver.quit()
            return
        else:
            print("Name match")
    except NoSuchElementException:
        print("No h3 element found. Exiting...")
        driver.quit()
        return


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
    time.sleep(10)  # This will pause the execution for 10 seconds


    # Close the browser
    driver.quit()

# Example usage
search_contact_info("EARL DES CANTALOUS", "LARODDE")
