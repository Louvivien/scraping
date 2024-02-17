import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

async def scrape_url(address, denominationUniteLegale):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.google.com/maps")
        print("Navigated to Google Maps successfully.")

        accept_button = await page.query_selector('[aria-label*="Accept"]')
        if accept_button:
            await accept_button.click()
            print("Accepted cookies.")

        await page.type('.searchboxinput', address)
        await page.press('.searchboxinput', 'Enter')
        print("Business search initiated.")

        # await asyncio.sleep(3)  # Example: 10 seconds

        try:
            await page.wait_for_selector('div[data-index="0"]', timeout=5000)
            await page.click('div[data-index="0"]')
            print("Option 1: Clicked on the first search result.")
        except:
            await page.wait_for_selector('div[jsaction*="mouseover:pane"]')
            await page.click('div[jsaction*="mouseover:pane"]:first-child')
            print("Option 2: Clicked on the first search result.")


        title_element = await page.query_selector('h1.DUwDvf.lfPIob')
        if title_element:
            title_text = await title_element.text_content()
            print(f"Extracted title text: '{title_text}'")
            print(f"Comparing with denominationUniteLegale: '{denominationUniteLegale}'")
            match = similar(title_text, denominationUniteLegale)
            print(f"Similarity match (case-insensitive): {match * 100:.2f}%")
            if match < 0.5:
                print("Search not matched.")
                await browser.close()
                return "Search not matched"
            else:
                print("Match found. Continuing to find current URL.")
        else:
            print("Title element not found.")
            await browser.close()
            return "Title element not found"



        # Wait for the page to load completely
        await page.wait_for_load_state()
        current_url = page.url  # Corrected line: removed the parentheses
        print(f"Current URL: {current_url}")



        # await asyncio.sleep(1)
        await browser.close()

        return current_url


async def main(start_row=0):
    df = pd.read_csv('/Users/vivien/Documents/Scraping/GmapScraper/brasseries_with_phones.csv')
    df.fillna('', inplace=True)
    df = df[df['denominationUniteLegale'].notna() & df['denominationUniteLegale'].ne('')]

    print(f"Starting from row: {start_row}")
    print(f"Number of rows in DataFrame after filtering: {len(df)}")

    df['url'] = ''  # Add a new column for the URL


    # Define the filename for the partial save
    partial_save_filename = '/Users/vivien/Documents/Scraping/GmapScraper/brasseries_with_url_partial.csv'

    for index, row in df[start_row:].iterrows():
        address = f"{row['denominationUniteLegale']} {row['complementAdresseEtablissement']} {row['numeroVoieEtablissement']} {row['indiceRepetitionEtablissement']} {row['typeVoieEtablissement']} {row['libelleVoieEtablissement']} {row['codePostalEtablissement']} {row['libelleCommuneEtablissement']}"
        try:
            current_url = await scrape_url(address, row['denominationUniteLegale'])
        except Exception as e:
            print(f"Error occurred while processing address: {address}. Error: {e}")
            current_url = 'Error'
        df.at[index, 'current_url'] = current_url

        # Every 10 rows, append the processed rows to the partial CSV
        if (index - start_row + 1) % 10 == 0:
            with open(partial_save_filename, 'a') as f:
                df[start_row:index+1].to_csv(f, header=f.tell()==0, index=False)
            print(f"Saved progress up to row {index+1}")

        print(f"Processed row {index+1}/{len(df)}")

    # Save the final DataFrame
    df.to_csv('/Users/vivien/Documents/Scraping/GmapScraper/brasseries_with_phones_and_url.csv', index=False)

start_row_number = 0  # Modify this to start from a different row
asyncio.run(main(start_row=start_row_number))