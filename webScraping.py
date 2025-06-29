import requests
import json
import os
from tqdm import tqdm

def run():
    """
    This script extracts all etikett numbers, adds it to the relevant url and downloads all the pdfs
    for each product and saves it in the folder "final_labels"
    """
    # Base URL without the addon
    base_url = "https://plantevernmidler.mattilsynet.no/api/etikett/"

    # Load the JSON data
    with open('godkjente_plantevernmidler_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract all unique registreringsnummer, skipping None values
    registreringsnummer_list = list({product['registreringsnummer'] for product in data['preparater'] if product['registreringsnummer']})

    # Print the number of registreringsnummer being processed
    print(f"Processing {len(registreringsnummer_list)} registreringsnummer.")

    # Create the final_labels directory if it doesn't exist
    output_directory = 'final_labels'
    os.makedirs(output_directory, exist_ok=True)

    # Loop through each registreringsnummer, construct the download URL, and save the PDF
    for registreringsnummer in tqdm(registreringsnummer_list, desc="Downloading PDFs", unit="file"):
        if registreringsnummer:  # Ensure registreringsnummer is not None
            # Construct the full URL using the original registreringsnummer (with dots)
            full_url = base_url + registreringsnummer

            # Download the PDF
            response = requests.get(full_url)

            if response.status_code == 200 and response.content:
                # Save the PDF in the final_labels directory with .pdf extension
                pdf_filename = registreringsnummer + ".pdf"
                pdf_path = os.path.join(output_directory, pdf_filename)

                with open(pdf_path, "wb") as file:
                    file.write(response.content)
            else:
                print(f"Failed to download {full_url} (status {response.status_code})")

if __name__ == "__main__":
    run()