import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def scrape_phone_number(address):
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

        await asyncio.sleep(60)





        try:
            await page.wait_for_selector('div[data-index="0"]', timeout=5000)
            await page.click('div[data-index="0"]')
            print("Option 1: Clicked on the first search result.")
        except:
            await page.wait_for_selector('div[jsaction*="mouseover:pane"]')
            await page.click('div[jsaction*="mouseover:pane"]:first-child')
            print("Option 2: Clicked on the first search result.")

        buttons = await page.query_selector_all('button')
        for index, button in enumerate(buttons):
            html = await button.inner_html()
            print(f"Processing Button {index}")

        phone_button = await page.query_selector('button.CsEnBe[data-item-id*="phone"]')
        if phone_button:
            phone_number = await phone_button.get_attribute('aria-label')
            phone_number = phone_number.replace('Phone: ', '')
        else:
            phone_number = 'Phone number not found'

        print(f'Phone Number: {phone_number}')

        # await asyncio.sleep(1)
        await browser.close()

        return phone_number


async def main(start_row=0):
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
            phone_number = await scrape_phone_number(address)
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
asyncio.run(main(start_row=start_row_number))