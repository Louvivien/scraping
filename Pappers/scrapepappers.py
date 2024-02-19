import asyncio
from playwright.async_api import async_playwright
import pandas as pd

# Load CSV file
df = pd.read_csv('/Users/vivien/Documents/Scraping/Pappers/Prosp_Brasseries_PDT.csv', delimiter=';')

# Add columns for the new data
df['Company Name'] = ''
df['Company Address'] = ''
df['Share Capital'] = ''

async def fetch_details(siret):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.pappers.fr/')
        
        print(f"Searching for SIRET: {siret}")
        await page.fill('input[type="search"][name="q"]', siret)
        await page.click('button:has-text("Rechercher")')
        await page.wait_for_selector('h1.big-text', timeout=5000)
        
        company_name = await page.text_content('h1.big-text')
        company_address = await page.text_content('tbody:nth-of-type(1) >> tr:has(th:has-text("Adresse :")) >> td')
        try:
            share_capital = await page.text_content('text="Capital social :" >> xpath=following-sibling::td', timeout=5000)
        except Exception:
            share_capital = "Not Found"
        
        print(f"Results for {siret}:")
        print(f"Company Name: {company_name}")
        print(f"Company Address: {company_address}")
        print(f"Share Capital: {share_capital if share_capital != 'Not Found' else 'Share Capital not found'}")
        
        await browser.close()
        return company_name.strip(), company_address.strip(), share_capital.strip()

async def main():
    for index, row in df.iterrows():
        siret = row['siret']
        company_name, company_address, share_capital = await fetch_details(str(siret))
        df.at[index, 'Company Name'] = company_name
        df.at[index, 'Company Address'] = company_address
        df.at[index, 'Share Capital'] = share_capital
        
        # Save partial results every 10 entries
        if (index + 1) % 10 == 0:
            partial_filename = f'/Users/vivien/Documents/Scraping/Pappers/Partial_Result_{index + 1}.csv'
            df.iloc[:index+1].to_csv(partial_filename, index=False, sep=';')
            print(f"Saved partial results to {partial_filename}")

    # Save final results
    final_filename = '/Users/vivien/Documents/Scraping/Pappers/Final_Result.csv'
    df.to_csv(final_filename, index=False, sep=';')
    print(f"Saved final results to {final_filename}")

if __name__ == '__main__':
    asyncio.run(main())
