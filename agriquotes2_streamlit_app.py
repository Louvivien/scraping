from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import streamlit as st
import pandas as pd

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

# Function to fetch and parse data, now accepts a URL parameter
def fetch_data(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script', type='text/javascript')
    pattern = re.compile(r'mydata\s*=\s*(\[\{.*?\}\])', re.DOTALL)

    for script in scripts:
        result = pattern.search(script.text)
        if result:
            json_str = result.group(1)
            data = json.loads(json_str)
            first_set = data[0]

            keys = list(first_set.keys())
            first_price_key = keys[1]
            first_price = first_set[first_price_key]
            return first_price
    return pd.NA

# Streamlit app
def main():
    st.title("Prix jour enlèvement jour")

    # Product-specific city lists with URLs
    products_cities = {
        "TOURTEAU COLZA (231)": [
            ("BASSENS (33)", 'URL8'), 
            ("BREST (29)", 'URL9'), 
            ("GAND", 'URL10'), 
            ("HUNINGUE (68)", 'URL11'), 
            ("MONTOIR-DE-BRETAGNE (44)", 'URL14'), 
            ("PASAJES", 'URL15'), 
            ("ROUEN (76)", 'URL16'), 
            ("SETE (34)", 'URL17'), 
            ("ST-MALO (35)", 'URL18'), 
            ("VERDUN (55)", 'URL19'), 
            ("LOWER RHINE", 'URL13'), 
            ("LE MÉRIOT (10)", 'URL12')
        ],
        "TOURTEAU COLZA EXPELLER FROID (235)": [
            ("BOOFZHEIM (67)", 'URL1'), 
            ("BOULAZAC (24)", 'URL2'), 
            ("DUN-SUR-AURON (18)", 'URL3'), 
            ("ERCUIS (60)", 'URL4'), 
            ("FRESNOY-EN-THELLE (60)", 'URL5'), 
            ("PAIZAY-LE-SEC (86)", 'URL6'), 
            ("ROYBON (38)", 'URL7')
        ],
        "TOURTEAU SOJA 48% (206)": [
            ("BARCELONE", 'URL20'), 
            ("BILBAO", 'URL21'), 
            ("BREST (29)", 'URL22'), 
            ("CHALON-SUR-SAONE (71)", 'URL23'), 
            ("GAND", 'URL24'), 
            ("HUNINGUE (68)", 'URL25'), 
            ("LA PALLICE (17)", 'URL26'), 
            ("LORIENT (56)", 'URL27'), 
            ("SETE (34)", 'URL28')
        ],
        "TOURTEAU SOJA 49 (202)": [
            ("BREST (29)", 'URL29'), 
            ("GAND", 'URL30'), 
            ("HUNINGUE (68)", 'URL31'), 
            ("ROTTERDAM", 'URL32')
        ],
        "TOURTEAU SOJA PCR 0.9% (203)": [
            ("BREST (29)", 'URL33'), 
            ("CHALON-SUR-SAONE (71)", 'URL34'), 
            ("GAND", 'URL35'), 
            ("LA PALLICE (17)", 'URL36'), 
            ("LORIENT (56)", 'URL37'), 
            ("MONTOIR-DE-BRETAGNE (44)", 'URL38'), 
            ("ROUEN (76)", 'URL39'), 
            ("SETE (34)", 'URL40')
        ],
        "DRECHES DE BLE (339)": [
            ("BAZANCOURT (51)", 'URL41'), 
            ("ORIGNY-STE-BENOITE (02)", 'URL42'), 
            ("ZEITZ", 'URL43')
        ],
        "TOURTEAU CANOLA (240)": [
            ("ROUEN (76)", 'URL44')
        ],
        "TOURTEAU TOURNESOL 28 (221)": [
            ("DEINZE", 'URL45'), 
            ("REUS", 'URL46'), 
            ("ST-NAZAIRE (44)", 'URL47')
        ],
    }


    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Fetch prices for each city and add to the DataFrame for all products
    for product, city_url_pairs in products_cities.items():
        row = {}
        for city, url_key in city_url_pairs:
            price = fetch_data(os.getenv(url_key))
            if price is not pd.NA:
                row[city] = price
        if row:  # Check if row is not empty
            df = pd.concat([df, pd.DataFrame(row, index=[product])])

    if not df.empty:
        df = df.fillna('')  # Replace <NA> with an empty string
        st.table(df)
    else:
        st.write("No data found.")

if __name__ == "__main__":
    main()
