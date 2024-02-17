import pandas as pd
from playwright.sync_api import sync_playwright
import os
import xlrd

def fetch_establishment_data(playwright, establishment):
    print(f"Processing establishment: {establishment}")
    context = playwright.chromium.launch(headless=False).new_context(accept_downloads=True)
    page = context.new_page()

    url = f"https://www.georisques.gouv.fr/risques/installations/donnees?page=1&etablissement={establishment.replace(' ', '%20')}"
    print(f"Navigating to URL: {url}")
    page.goto(url)
    page.wait_for_timeout(5000)

    result = "No result"
    try:
        first_cell_selector = 'tbody tr:first-child td a'
        if page.is_visible(first_cell_selector):
            print("Clicking on the first cell...")
            page.click(first_cell_selector)
            page.wait_for_timeout(5000)
            new_tab = context.pages[-1]
            new_tab.bring_to_front()

            download_link_selector = 'p[align="right"] a'
            print("Attempting to download file...")
            with new_tab.expect_download() as download_info:
                new_tab.click(download_link_selector)
            download = download_info.value
            file_path = download.path()
            download.save_as(file_path)
            print(f"File downloaded to: {file_path}")

            # Read the .xls file using xlrd
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)  # Assuming you want the first sheet
            result = sheet.cell_value(1, 2)  # Get the value of cell C2 (row 2, col 3)
            print(f"Result obtained: {result}")

            os.remove(file_path)
            print("Downloaded file deleted.")
        else:
            print("First cell not found, marking as 'No result'.")
    except Exception as e:
        print(f"Error while processing {establishment}: {e}")
    finally:
        context.close()

    return result

# Use the CSV file
file_path = '/Users/vivien/Documents/Scraping/Georisques/Liste-_-METHA2.csv'

# Load the CSV file into a DataFrame
try:
    df = pd.read_csv(file_path, encoding='utf-8', delimiter=';')  # Specify the delimiter as ';'
    print("CSV file loaded into DataFrame.")
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit()

# Add a new column 'Result'
df['Result'] = ''



with sync_playwright() as playwright:
    for index, row in df.iterrows():
        establishment = row['Nom du partenaire']
        result = fetch_establishment_data(playwright, establishment)
        df.at[index, 'Result'] = result
        print(f"Updated result for '{establishment}': {result}")

# Save the updated DataFrame
output_file_path = '/Users/vivien/Documents/Scraping/Georisques/Liste-_-METHA2_Updated.xlsx'
df.to_excel(output_file_path, index=False, engine='openpyxl')  # Ensure 'openpyxl' is installed for .xlsx support
print(f"Updated file has been saved to: {output_file_path}")
