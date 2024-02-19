from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Launch browser in non-headless mode
        page = await browser.new_page()
        await page.goto('https://www.pappers.fr/')
        
        async with page.expect_navigation():
            await page.fill('input[type="search"][name="q"]', '41310744200027')
            await page.click('button:has-text("Rechercher")')
        
        # Ensure the page has fully loaded by waiting for a known element that appears on the result page
        await page.wait_for_selector('h1.big-text')  # Example selector, adjust based on actual content
        
        company_name = await page.text_content('h1.big-text')
        print(f"Company Name: {company_name.strip()}")  # Use .strip() to remove leading/trailing whitespace
        
        company_address = await page.text_content('tbody:nth-of-type(1) >> tr:has(th:has-text("Adresse :")) >> td')
        print(f"Company Address: {company_address.strip()}")  # Use .strip() to remove leading/trailing whitespace
        
        # Adjust the selector based on actual inspection of the page structure for the share capital
        # For debugging, let's just ensure we're targeting something existing or adjust the logic to find the correct element
        try:
            share_capital = await page.text_content('text="Capital social :" >> xpath=following-sibling::td', timeout=5000)
            print(f"Share Capital: {share_capital.strip()}")  # Use .strip() to remove leading/trailing whitespace
        except Exception as e:
            print(f"Failed to find share capital: {str(e)}")

        # Uncomment to keep the browser open
        # await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
