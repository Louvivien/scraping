import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Function to fetch and parse data
def fetch_data():
    url = os.getenv('URL')
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

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script', type='text/javascript')
    pattern = re.compile(r'mydata\s*=\s*(\[\{.*?\}\])', re.DOTALL)

    for script in scripts:
        result = pattern.search(script.text)
        if result:
            json_str = result.group(1)
            data = json.loads(json_str)
            return data[:365]  # Return the first two sets of data

# Function to transform data into a DataFrame
def transform_data(data):
    # Initialize an empty list to hold the transformed data
    transformed_data = []
    
    # Iterate over each item in the data
    for item in data:
        # Initialize a row with the 'date' column
        row = {'date': item['date']}
        
        # Iterate over each key-value pair in the item
        for key, value in item.items():
            # Check if the key does not contain 'state' and is not 'date'
            if 'state' not in key and key != 'date':
                # Convert the key to the desired format (MM-YY)
                # Ensure the key format conversion is correctly applied
                if len(key) == 10:  # Expected format like "01_03_2024"
                    new_key = key[3:5] + '-' + key[8:10]
                else:
                    new_key = key  # Use the original key if it doesn't match the expected format
                # Add the value to the row under the new key
                row[new_key] = value
        
        # Append the row to the list of transformed data
        transformed_data.append(row)
    
    # Convert the list of transformed data into a DataFrame
    df = pd.DataFrame(transformed_data)
    return df


# Streamlit app
def main():
    st.title('TOURTEAU COLZA EXPELLER FROID - ROYBON (38)')

    data = fetch_data()

    if data:
        df = transform_data(data)
        st.table(df)
    else:
        st.write("No data found.")

if __name__ == "__main__":
    main()
