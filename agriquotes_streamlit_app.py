from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import streamlit as st

# Load environment variables
load_dotenv()

# Construct headers from environment variables
headers = {
    "Accept": os.getenv("ACCEPT"),
    "Accept-Language": os.getenv("ACCEPT_LANGUAGE"),
    "Connection": os.getenv("CONNECTION"),
    "Cookie": os.getenv("COOKIE"),
    "Referer": os.getenv("REFERER"),
    "Sec-Fetch-Dest": os.getenv("SEC_FETCH_DEST"),
    "Sec-Fetch-Mode": os.getenv("SEC_FETCH_MODE"),
    "Sec-Fetch-Site": os.getenv("SEC_FETCH_SITE"),
    "User-Agent": os.getenv("USER_AGENT"),
    "X-Requested-With": os.getenv("X_REQUESTED_WITH"),
    "sec-ch-ua": os.getenv("SEC_CH_UA"),
    "sec-ch-ua-mobile": os.getenv("SEC_CH_UA_MOBILE"),
    "sec-ch-ua-platform": os.getenv("SEC_CH_UA_PLATFORM"),
}

# Function to fetch and parse data
def fetch_data():
    url = os.getenv('URL')
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script', type='text/javascript')
    pattern = re.compile(r'mydata\s*=\s*(\[\{.*?\}\])', re.DOTALL)

    for script in scripts:
        result = pattern.search(script.text)
        if result:
            json_str = result.group(1)
            data = json.loads(json_str)
            return data[:2]  # Return the first two sets of data

# Streamlit app
def main():
    st.title('TOURTEAU COLZA EXPELLER FROID - ROYBON (38)')

    data = fetch_data()

    if data:
        st.json(data)
    else:
        st.write("No data found.")

if __name__ == "__main__":
    main()
