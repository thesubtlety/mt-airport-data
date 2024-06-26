import pdfplumber
import pandas as pd
import requests
import os
import sys
import re
from pdf2image import convert_from_path

pdf_url = 'https://www.mdt.mt.gov/other/webdata/external/aero/airport-directory.pdf'
mt_pdf_path = 'directories/montana-directory.pdf'
outfile = 'airport_info_mt.csv'

def extract_airport_info(i, text):
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



        identmatch = re.search(r'IDENT:\s(\w\w\w)', text)
        if identmatch:
            ident = identmatch.group(1).replace("Ø","0")

        nme = lines[-1]

        print(nme)
        print(ident)

        if len(ident) > 4 or len(ident) < 3:
            print(f"Error parsing page {i} ({nme})")
            #return #ignore for now, manually fix
        else:
            airport_info["Airport Identifier"] = ident.strip().replace("Ø","0")
            airport_info["Airport Name"] = nme.strip()
    
    for line in lines:
        # Extracting the identifier
        if "IDENT:" in line:
            parts = line.split()
            ident_index = parts.index("IDENT:") + 1
            if ident_index < len(parts):
                airport_info["Airport Identifier"] = parts[ident_index]
        # Check for amenities
        if "rental" in line.lower() or "courtesy" in line.lower() or "crew car" in line.lower():
            airport_info["Courtesy Car"] = "Yes"
        if "camping" in line.lower() or "campsite" in line.lower() or "cabins" in line.lower():
            airport_info["Camping"] = "Yes"
        mealmatch = re.search(r'service:.+[A-Za-z]\s[½¼1]|adjacent|on field', line.lower())
        if mealmatch:
            airport_info["Meals"] = "Yes"
        if "bicycles" in line.lower() or "bikes" in line.lower():
            airport_info["Bicycles"] = "Yes"
    return airport_info

def save_image(pdf_path, pageNum, name):
    images = convert_from_path(pdf_path, first_page=pageNum+1, last_page=pageNum+1) #0-based
    for i, image in enumerate(images):
        image.save(f'images_mt/{name}.png', 'PNG')

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

def main():
    pdf_path = mt_pdf_path
    airport_data = []

    if not os.path.exists(pdf_path):
        download_pdf(pdf_url, mt_pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")

        start_page = 36
        end_page = 157

        for i, page in enumerate(pdf.pages[start_page-1:], start=start_page):
            if i > (total_pages - (total_pages-end_page)):
                break

            text = page.extract_text()
            if text:
                airport_info = extract_airport_info(i, text)
                if airport_info:
                    if id == "8S1": airport_info["Courtesy Car"] = "Yes" #not listed for some reason
                    airport_data.append(airport_info)
                    id = airport_info.get("Airport Identifier")
                    if id: save_image(pdf_path, i, id)
                    
    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(airport_data)
    
    # Print the DataFrame
    print(df)

    df.to_csv(outfile, index=False)
    print(f"Data saved to {outfile}")

if __name__ == "__main__":
    main()
