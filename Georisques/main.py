from playwright.sync_api import sync_playwright
import os
import xlrd

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    establishment = "BIOMETHANE DU CHAUNOIS"
    url = f"https://www.georisques.gouv.fr/risques/installations/donnees?page=1&etablissement={establishment.replace(' ', '%20')}"
    page.goto(url)
    page.wait_for_timeout(5000)

    first_cell_selector = 'tbody tr:first-child td a'
    page.click(first_cell_selector)
    print("Clicked on first cell, waiting for new tab...")

    page.wait_for_timeout(5000)
    new_tab = context.pages[-1]
    new_tab.bring_to_front()

    download_link_selector = 'p[align="right"] a'
    with new_tab.expect_download() as download_info:
        new_tab.click(download_link_selector)
    download = download_info.value
    file_path = str(download.path()) + ".xls"  # Assume it's an .xls file for compatibility
    download.save_as(file_path)
    print(f"File downloaded and renamed for compatibility: {file_path}")

    # Read the .xls file using xlrd
    try:
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(2)  # Assuming you want the first sheet
        cell_value = sheet.cell_value(1, 2)  # Get the value of cell C2 (row 2, col 3)
        print(f"Data in cell C2: {cell_value}")
    except Exception as e:
        print(f"Error reading Excel file with xlrd: {e}")

    # Cleanup: Delete the downloaded file
    try:
        os.remove(file_path)
        print(f"Deleted downloaded file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
