import pdfplumber
import pandas as pd
import requests
import os
import sys
import re
from pdf2image import convert_from_path
from PIL import Image


fl_url = ''
id_url = 'https://itd.idaho.gov/wp-content/uploads/2020/08/Airport-Facilities-Directory.pdf'
md_url = 'https://marylandregionalaviation.aero/wp-content/uploads/2023/09/Airport%20Directory%202023-24.pdf'
mn_url = 'https://www.dot.state.mn.us/aero/airportdirectory/documents/2024_Airport_Directory_and_Travel_Guide_23JAN24_lowres.pdf'
nd_url = ''
sd_url = ''
or_url = ''
tx_url = ''
wi_url = 'https://wisconsindot.gov/Documents/travel/air/airport-info/arptdir-all.pdf'
wy_url = 'https://drive.google.com/file/d/1s04nV-sgQ0J5bsz9d9yyxE2I1RP3k0ao/view'

airports_url = 'https://davidmegginson.github.io/ourairports-data/airports.csv'
airports_path = 'data/airports.csv'

def extract_page_info(page, text, state):
    # Initialize dictionary to hold extracted info
    airport_info = {
        "Airport Identifier": "",
        "Airport Name": "",
        "Courtesy Car": "No",
        "Bicycles": "No",
        "Camping": "No",
        "Meals": "No"
    }

    #import pdb
    #pdb.set_trace()

    match state:
        case "id":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming the first line contains the airport name
                name = ",".join(lines[0:1])
                ident = name.split(' ')[-1]
                nme = " ".join(name.split(' ')[0:-1])
                print(nme)
                print(ident)

                if len(ident) > 4 or len(ident) < 3:
                    print(f"Error parsing page {page} ({name})")
                    #return #ignore for now, manually fix
                else:
                    airport_info["Airport Identifier"] = ident.replace("Ø","0")
                    airport_info["Airport Name"] = nme
            
            for line in lines:
                # Check for amenities
                if "rental" in line.lower() or "courtesy" in line.lower() or "crew car" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                if "camping" in line.lower() or "campground" in line.lower():
                    airport_info["Camping"] = "Yes"
                if "meals" in line.lower() or "food" in line.lower():
                    airport_info["Meals"] = "Yes"
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "fl":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming one of these lines contains the airport name
                identifier = " ".join(lines[0:4])
                identmatch = re.search(r'Identifier\ (....?)\ ', identifier)
                if identmatch:
                    ident = identmatch.group(1)

                nme = lines[1]

                print(nme)
                print(ident)

                if len(ident) > 4 or len(ident) < 3:
                    print(f"Error parsing page {page} ({nme})")
                    #return #ignore for now, manually fix
                else:
                    airport_info["Airport Identifier"] = ident.strip().replace("Ø","0")
                    airport_info["Airport Name"] = nme.strip()
            
            for line in lines:
                # Check for amenities
                if "rental car yes" in line.lower() or "courtesy car yes" in line.lower() or "crew car yes" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                if "camping" in line.lower():
                    airport_info["Camping"] = "Yes"
                if "dining yes" in line.lower() or "restaurant" in line.lower():
                    airport_info["Meals"] = "Yes"
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "wy":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming one of these lines contains the airport name
                name = lines[-1]+lines[-2]+lines[0]+lines[1]
                identmatch = re.search(r'\((.*?)\)', name)
                if identmatch:
                    ident = identmatch.group(1)

                namematch = re.search(r'[/,]\s*([^/(]+)\s*\(', text)
                if namematch:
                    nme = namematch.group(1)

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
                if "rental" in line.lower() or "courtesy car" in line.lower() or "crew car" in line.lower() or "transportation" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                if "camping" in line.lower():
                    airport_info["Camping"] = "Yes"
                if "food-lodging(1mi)" in line.lower() or "food(1mi)" in line.lower() or "food(1/2mi)" in line.lower() or "food on field" in line.lower() or "restaurant" in line.lower():
                    airport_info["Meals"] = "Yes"
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "md":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming one of these lines contains the airport name
                nme = lines[0]
                if "St. Mary’s" in nme: nme = "St. Mary's" # why
                if "/" in nme: nme = lines[0].split('/')[-1].strip()
                if "-" in nme: nme = lines[0].split('-')[-1].strip()
                identstr = "_"+ "_".join(lines[-15:-1])+"_" # wow
                print(identstr)
                idmatch = re.search(r"[_\/-]{}.*?(\w\w\w)_".format(re.escape(nme)), identstr)
                if idmatch:
                    ident = idmatch.group(1)        
                
                print(nme)
                print(ident)

                if len(ident) > 4 or len(ident) < 3:
                    print(f"Error parsing page {page} ({nme})")
                    #return #ignore for now, manually fix
                else:
                    airport_info["Airport Identifier"] = ident.strip().replace("Ø","0")
                    airport_info["Airport Name"] = nme.strip()
            
            for line in lines:
                # Check for amenities
                if "rental" in line.lower() or "courtesy" in line.lower() or "crew car" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                if "camping" in line.lower():
                    airport_info["Camping"] = "Yes"
                if "restaurant" in line.lower():
                    airport_info["Meals"] = "Yes"
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "mn":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming one of these lines contains the airport name
                name = lines[0]
                identmatch = re.search(r'\w+\s-\s(\w+)', name)
                if identmatch:
                    ident = identmatch.group(1)

                namematch = re.search(r'(\w+)\s-\s\w+', name)
                if namematch:
                    nme = namematch.group(1)

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
                if "courtesy car" in line.lower() or "crew car" in line.lower() or "transportation" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                campmatch = re.search(r'campgrounds:.+\s[½¼1]|underwing camp: yes', line.lower()) 
                if campmatch:
                    airport_info["Camping"] = "Yes"
                
                mealmatch = re.search(r'dining:.+\s[½¼1]', line.lower()) 
                if mealmatch:
                    airport_info["Meals"] = "Yes"
                
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "mt":
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
            
            if airport_info["Airport Identifier"] == "8S1":
                airport_info["Courtesy Car"] = "Yes"

            return airport_info
        case "nd":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming one of these lines contains the airport name
                ident = lines[1]
                nme = lines[2]

                print(nme)
                print(ident)

                if len(ident) > 4 or len(ident) < 3:
                    print(f"Error parsing page {page} ({nme})")
                    #return #ignore for now, manually fix
                else:
                    airport_info["Airport Identifier"] = ident.strip().replace("Ø","0")
                    airport_info["Airport Name"] = nme.strip()
            
            for line in lines:
                if "rental" in line.lower() or "courtesy car" in line.lower() or "transportation" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                
                campmatch = re.search(r'campgrounds:.+\s[½¼1]|underwing camp: yes', line.lower()) 
                if campmatch:
                    airport_info["Camping"] = "Yes"
                
                mealmatch = re.search(r'dining:.+\s[½¼1]', line.lower()) 
                if mealmatch:
                    airport_info["Meals"] = "Yes"
                
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "or":
            return "not implemented"
        case "sd":
            lines = text.split('\n')
            print(lines)
            if lines:
                # Assuming one of these lines contains the airport name
                namestr = lines[0]
                ident = namestr.split(" ")[-1]
                nme = " ".join(namestr.split(" ")[1:-1])

                print(nme)
                print(ident)

                if len(ident) > 4 or len(ident) < 3:
                    print(f"Error parsing page {page} ({nme})")
                    #return #ignore for now, manually fix
                else:
                    airport_info["Airport Identifier"] = ident.strip().replace("Ø","0")
                    airport_info["Airport Name"] = nme.strip()
            
            for line in lines:
                # Check for amenities
                if "rental" in line.lower() or "courtesy" in line.lower() or "crew car" in line.lower():
                    airport_info["Courtesy Car"] = "Yes"
                if "camping" in line.lower():
                    airport_info["Camping"] = "Yes"
                if "dining: " in line.lower():
                    airport_info["Meals"] = "Yes"
                if "bicycles" in line.lower() or "bikes" in line.lower():
                    airport_info["Bicycles"] = "Yes"

            return airport_info
        case "tx":
                lines = text.split('\n')
                print(lines)
                if lines:
                    # Assuming one of these lines contains the airport name
                    name = lines[-1]+lines[-2]+lines[0]+lines[1]
                    identmatch = re.search(r'\((.*?)\)', name)
                    if identmatch:
                        ident = identmatch.group(1)

                    namematch = re.search(r'[/,]\s*([^/(]+)\s*\(', text)
                    if namematch:
                        nme = namematch.group(1)

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
                    if "rental" in line.lower() or "courtesy car" in line.lower() or "crew car" in line.lower() or "transportation" in line.lower():
                        airport_info["Courtesy Car"] = "Yes"
                    if "camping" in line.lower() or "cabins" in line.lower():
                        airport_info["Camping"] = "Yes"
                    mealmatch = re.search(r'FOOD-LODGING\([½¼1]MI|1\/2MI|1\/4 ?MI|1\/2|ON FIELD\)', line) 
                    if mealmatch:
                        airport_info["Meals"] = "Yes"
                    if "bicycles" in line.lower() or "bikes" in line.lower():
                        airport_info["Bicycles"] = "Yes"

                return airport_info
        case "wi":
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
        case _:
            return "Not implemented"  
        
def parse_state(airport_data, state, directory_url, method, start_page, end_page):
    pdf = f'directories/{state}.pdf'
    out = f'data/airport_info_{state}.csv'
    imgDir = f'images/{state}/'

    # dl if we need 
    if not os.path.exists(pdf):
        download_pdf(directory_url, pdf)

    with pdfplumber.open(pdf) as pdff:
        total_pages = len(pdff.pages)
        print(f"Total pages: {total_pages}")
        if method == "pairs":
            for i in range(start_page - 1, total_pages - (total_pages - end_page) - 1): # pairs of pages
                if (i - start_page + 1) % 2 == 0:  # every other
                    current_page_text = pdff.pages[i].extract_text() if pdff.pages[i] else ""
                    next_page_text = pdff.pages[i + 1].extract_text() if i + 1 < len(pdff.pages) else ""  # Handle the last page case
                    text = current_page_text + " " + next_page_text
                    if text:
                        airport_info = extract_page_info(i, text, state)
                        if airport_info:
                            airport_data.append(airport_info)
                            id = airport_info.get("Airport Identifier")
                            if id:
                                save_combined_image(pdf, i + 1, i + 2, id, imgDir)  # Adjust indices as necessary
                if i >= (total_pages - (total_pages - end_page) - 1):  # Check if it's time to break after processing pairs
                    break
        else:
            for i, page in enumerate(pdff.pages[start_page-1:], start=start_page):
                text = page.extract_text()
                if text:
                    airport_info = extract_page_info(i, text, state)
                    if airport_info:
                        airport_data.append(airport_info)
                        id = airport_info.get("Airport Identifier")
                        if id: save_image(pdf, i, id, imgDir)
                if i > (total_pages - (total_pages-end_page)):
                    break
            

    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(airport_data)
    
    # Print the DataFrame
    print(df)

    df.to_csv(out, index=False)
    print(f"Data saved to {out}")

def save_combined_image(pdf_path, start_page, end_page, name, imgdir):
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)

    # Convert pages to images
    images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
    images = [image.rotate(270, expand=True) for image in images] #to rotate

    # Assuming images are not empty and have the same width
    total_height = sum(image.height for image in images)
    max_width = max(image.width for image in images)
    
    # Create a new image with the combined height of the two pages
    combined_image = Image.new('RGB', (max_width, total_height))
    
    # Paste the images into the combined image
    y_offset = 0
    for image in images:
        combined_image.paste(image, (0, y_offset))
        y_offset += image.height
    
    # Save the combined image
    combined_image_filename = f"{imgdir}{name}.png"
    combined_image.save(combined_image_filename, 'PNG')

def save_image(pdf_path, pageNum, name, imgdir):
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

def main():

    airport_data = []
    if not os.path.exists(airports_path):
        download_pdf(airports_url, airports_path)

    sys.exit(1)

    parse_state(airport_data, "id", id_url, "single", 38, 182)
    parse_state(airport_data, "fl", id_url, "single", 11, 138)
    parse_state(airport_data, "md", mn_url, "pairs", 11, 78)
    parse_state(airport_data, "mn", mn_url, "pairs", 22, 293)
    parse_state(airport_data, "mt", id_url, "single", 36, 157)
    parse_state(airport_data, "or", mn_url, "pairs", 13, 221)
    parse_state(airport_data, "mt", id_url, "single", 36, 157)
    parse_state(airport_data, "sd", id_url, "pairs", 36, 175)
    parse_state(airport_data, "tx", wy_url, "single", 24, 411)
    parse_state(airport_data, "wa", wy_url, "single", 10, 138)
    parse_state(airport_data, "wi", wy_url, "single", 35, 177)
    parse_state(airport_data, "wy", wy_url, "pairs", 12, 91)

if __name__ == "__main__":
    main()
