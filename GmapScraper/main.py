import asyncio
from playwright.async_api import async_playwright

async def scrape_phone_number():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True to run without a browser UI
        page = await browser.new_page()

        # Navigate to Google Maps
        await page.goto("https://www.google.com/maps")
        print("Navigated to Google Maps successfully.")

        # Accept Cookies if the button exists
        accept_button = await page.query_selector('[aria-label*="Accept"]')
        if accept_button:
            await accept_button.click()
            print("Accepted cookies.")

        # Search for the business
        await page.type('.searchboxinput', 'CERES BP 89	185		RUE	LEO LAGRANGE	59500	DOUAI')
        await page.press('.searchboxinput', 'Enter')
        print("Business search initiated.")

        # Here there are two possibilities
        # Option 1: find a div with data-index="0" and click on it
        # Option 2: Wait for the search results to load and click on the first div with jsaction containing "mouseover:pane"
        try:
            # Attempt Option 1
            await page.wait_for_selector('div[data-index="0"]', timeout=5000)
            await page.click('div[data-index="0"]')
            print("Option 1: Clicked on the first search result.")
        except:
            # Fallback to Option 2
            await page.wait_for_selector('div[jsaction*="mouseover:pane"]')
            await page.click('div[jsaction*="mouseover:pane"]:first-child')
            print("Option 2: Clicked on the first search result.")

        # Process each button's HTML (required for DOM updates), but minimize output
        buttons = await page.query_selector_all('button')
        for index, button in enumerate(buttons):
            html = await button.inner_html()
            print(f"Processing Button {index}")  # Minimal output, just an identifier

        # Extract phone number
        phone_button = await page.query_selector('button.CsEnBe[data-item-id*="phone"]')
        if phone_button:
            phone_number = await phone_button.get_attribute('aria-label')
            phone_number = phone_number.replace('Phone: ', '')  # Cleaning up the extracted phone number
        else:
            phone_number = 'Phone number not found'

        print(f'Phone Number: {phone_number}')

        # Wait for 1 minutes
        print("Waiting for 1 minute...")
        await asyncio.sleep(60) 



        await browser.close()

asyncio.run(scrape_phone_number())
