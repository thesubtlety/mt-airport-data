import pdfplumber
import pandas as pd
import requests
import os
import re
from pdf2image import convert_from_path

'''
update page nums
update data terms
'''

pdf_url = 'https://wisconsindot.gov/Documents/travel/air/airport-info/arptdir-all.pdf'
pdf_path = 'directories/wisconsin-directory.pdf'
outputf = 'airport_info_wi.csv'
imgdir = 'images_wi/'

airports_url = 'https://davidmegginson.github.io/ourairports-data/airports.csv'
airports_path = 'airports.csv'

def save_image(pdf_path, pageNum, name):
    if not os.path.exists(f'{imgdir}'):
        os.makedirs(imgdir)

    images = convert_from_path(pdf_path, first_page=pageNum, last_page=pageNum)
    for i, image in enumerate(images):
        image.save(f'{imgdir}{name}.png', 'PNG')

def download_pdf(url, save_path):
    print(f"Downloading pdf from {url}")
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Open the file path as a binary file and write the content
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"PDF successfully downloaded and saved as '{save_path}'.")
        else:
            print(f"Failed to download the PDF. HTTP status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred downloading file: {e}")

def extract_airport_info(page, text):
    # Initialize dictionary to hold extracted info
    airport_info = {
        "Airport Identifier": "",
        "Airport Name": "",
        "Courtesy Car": "No",
        "Bicycles": "No",
        "Camping": "No",
        "Meals": "No"
    }
    
    # Split text into lines for easier processing
    lines = text.split('\n')
    print(lines)
    if lines:
        # Assuming one of these lines contains the airport name
        name = " ".join(lines[0:2])
        print(name)
        identmatch = re.search(r'\((.*?)\)', name)
        if identmatch:
            ident = identmatch.group(1)

        namematch = re.search(r'\d+\s?\d?\s+(.*?)\s+\(', name)
        if namematch:
            nme = namematch.group(1)

        if "Airport Diagram" in nme:
            return
        
        print(nme)
        print(ident)

        if len(ident) > 4 or len(ident) < 3:
            print(f"Error parsing page {page} ({name})")
            #return #ignore for now, manually fix
        else:
            airport_info["Airport Identifier"] = ident.strip().replace("Ø","0")
            airport_info["Airport Name"] = nme.strip()
    
    for line in lines:
        # Check for amenities
        if "rental" in line.lower() or "courtesy car" in line.lower() or "crew car" in line.lower():
            airport_info["Courtesy Car"] = "Yes"
        if "camping" in line.lower():
            airport_info["Camping"] = "Yes"
        if "food" in line.lower() or "restaurant" in line.lower():
            airport_info["Meals"] = "Yes"
        if "bicycles" in line.lower() or "bikes" in line.lower():
            airport_info["Bicycles"] = "Yes"

    return airport_info

def main():
    airport_data = []

    if not os.path.exists(pdf_path):
        download_pdf(pdf_url, pdf_path)
        download_pdf(airports_url, airports_path)

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")

        start_page = 35
        end_page = 177

        #import pdb
        #pdb.set_trace()
        for i, page in enumerate(pdf.pages[start_page-1:], start=start_page):
            if i > (total_pages - (total_pages-end_page)):
                break

            text = page.extract_text()
            if text:
                airport_info = extract_airport_info(i, text)
                if airport_info:
                    airport_data.append(airport_info)
                    id = airport_info.get("Airport Identifier")
                    if id: save_image(pdf_path, i, id)
                    
    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(airport_data)
    
    # Print the DataFrame
    print(df)

    df.to_csv(outputf, index=False)
    print(f"Data saved to {outputf}")

    #todo fix up with modifications before writing to file

if __name__ == "__main__":
    main()

'''
Fixes (due to pdf text extraction issues)
Copy paste into airport_info_state.csv before converting to json

EVW,Uinta County Airport,Yes,No,No,No
RKS,Southwest Wyoming Regional Airport,Yes,No,No,No

'''