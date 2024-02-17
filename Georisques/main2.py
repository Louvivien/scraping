import csv
import requests
from bs4 import BeautifulSoup

# Define the path to your original and new CSV files
original_csv_file_path = '/Users/vivien/Documents/Scraping/Georisques/Liste-_-METHA2.csv'
new_csv_file_path = '/Users/vivien/Documents/Scraping/Georisques/Updated_Liste-_-METHA2.csv'

# Open the original CSV file to read and the new CSV file to write
with open(original_csv_file_path, mode='r', encoding='utf-8') as csvfile, \
     open(new_csv_file_path, mode='w', encoding='utf-8', newline='') as newfile:
    
    csvreader = csv.DictReader(csvfile, delimiter=';')
    fieldnames = csvreader.fieldnames + ['Detail URL', 'Second TD Content']  # Add new columns
    csvwriter = csv.DictWriter(newfile, fieldnames=fieldnames, delimiter=';')
    
    csvwriter.writeheader()
    
    for row in csvreader:
        nom_du_partenaire = row['Nom du partenaire']
        detail_url = ''  # Default empty string
        second_td_content = ''  # Default empty string
        
        # Define the API endpoint and headers
        url = "https://georisques.gouv.fr/webappReport/ws/installations/sites/_search"
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7',
            'origin': 'https://www.georisques.gouv.fr',
            'referer': 'https://www.georisques.gouv.fr/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        params = {
            'page': '1',
            'etablissement': nom_du_partenaire,
            'fieldOrderBy': 'etab',
            'orderByAsc': 'true',
            'size': '10',
            'start': '0'
        }

        try:
            # Make the GET request
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            # Extract the numeroInspection value
            if data.get("data"):
                numero_inspection = data["data"][0].get("numeroInspection", "")
                detail_url = f"https://www.georisques.gouv.fr/risques/installations/donnees/details/{numero_inspection}"
                response = requests.get(detail_url)
                html_content = response.text

                # Parse the HTML content
                soup = BeautifulSoup(html_content, 'lxml')
                tbodies = soup.find_all('tbody')

                if len(tbodies) >= 2:
                    second_tbody = tbodies[1]
                    tds = second_tbody.find_all('td')
                    if len(tds) >= 2:
                        second_td = tds[1]
                        second_td_content = second_td.text.strip()
            else:
                print(f"No data found for {nom_du_partenaire}.")

        except Exception as e:
            print(f"An error occurred while processing {nom_du_partenaire}: {e}")

        # Add the new data to the row
        row['Detail URL'] = detail_url
        row['Second TD Content'] = second_td_content
        
        # Write the updated row to the new CSV file
        csvwriter.writerow(row)
