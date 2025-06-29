import json
import re
from crops_diseases import crops, diseases

def run():
    """
    * Constructs relevant functions to extract crops and diseases from information already in the JSON file
    * Reads the "extracted_sentences" file and extracts crops and diseases, and saves these in a dictionary
    * Reads in the JSON file, and runs through "offlabel" and "minor use" and extracts crops and diseases respectively
    * Adds both the normal allowance, offlabel and minor use to the json file
    """
    # Define the functions for extracting crops and diseases
    def extract_crops_from_sentence(sentence, crops):
        found_crops = []
        for crop in crops:
            if re.search(rf'\b{crop}\b', sentence, re.IGNORECASE):
                found_crops.append(crop)
        return found_crops

    def extract_diseases_from_paragraph(paragraph, diseases):
        found_diseases = []
        for disease in diseases:
            if re.search(rf'\b{disease}\b', paragraph, re.IGNORECASE):
                found_diseases.append(disease)
        return found_diseases

    # Read the extracted data from the text file
    extracted_data_file_path = 'extracted_sentences.txt'
    with open(extracted_data_file_path, 'r', encoding='utf-8') as file:
        extracted_data = file.read().split("\n\n")

    # Create a list to store processed data
    data_list = []
    for block in extracted_data:
        if block.strip():
            lines = block.splitlines()
            file_match = re.search(r'File:\s*(.+?)\.pdf', lines[0])
            if file_match:
                registration_number = file_match.group(1)
                
                crops_line = next((line for line in lines if line.startswith("Crops:")), None)
                diseases_line = next((line for line in lines if line.startswith("Diseases:")), None)
                
                crops_from_file = eval(crops_line.split(":", 1)[1].strip()) if crops_line else []
                diseases_from_file = eval(diseases_line.split(":", 1)[1].strip()) if diseases_line else []
                
                data_list.append({
                    "registration number": registration_number,
                    "Normal allowance": {
                        "crops": crops_from_file,
                        "diseases": diseases_from_file
                    }
                })

    # Read the existing JSON data
    json_file_path = 'godkjente_plantevernmidler_data.json'
    with open(json_file_path, 'r', encoding='utf-8') as file:
        godkjente_data = json.load(file)

    # Process and update JSON with new information
    for product in godkjente_data['preparater']:
        registration_number = product['registreringsnummer']
        
        # Extract crops and diseases from the off-label information
        offlabel_crops = []
        offlabel_diseases = []
        
        minorUse_crops = []
        minorUse_diseases = []
        
        for offlabel in product.get('offLabelGodkjenninger', []):
            merknad = offlabel.get('merknad', '')
            
            # Extract crops and diseases from the 'merknad' field
            extracted_crops = extract_crops_from_sentence(merknad, crops)
            extracted_diseases = extract_diseases_from_paragraph(merknad, diseases)
            
            offlabel_crops.extend(extracted_crops)
            offlabel_diseases.extend(extracted_diseases)
        
        
        for minorUse in product.get("minorUseUtvidelser", []):
            merknad = minorUse.get("merknad", "") or ''
            
            extracted_crops = extract_crops_from_sentence(merknad, crops)
            extracted_diseases = extract_diseases_from_paragraph(merknad, diseases)
            
            minorUse_crops.extend(extracted_crops)
            minorUse_diseases.extend(extracted_diseases)
        
        # Deduplicate crops and diseases
        offlabel_crops = sorted(set(offlabel_crops))
        offlabel_diseases = sorted(set(offlabel_diseases))
        
        minorUse_crops = sorted(set(minorUse_crops))
        minorUse_diseases = sorted(set(minorUse_diseases))
        
        # Look for matching registration number in the text file data
        matching_data = next((item for item in data_list if item['registration number'] == registration_number), None)
            
        if matching_data:
            # Combine and deduplicate crops and diseases from both sources
            normal_crops = matching_data['Normal allowance']['crops']
            normal_diseases = matching_data["Normal allowance"]["diseases"]
            
            # Update the product with the combined information
            product['Normal allowance'] = {
                "crops": normal_crops,
                "diseases": normal_diseases
            }
        else:
            # If no match in the text file, just use the offlabel data
            product['Normal allowance'] = {
                "crops": offlabel_crops,
                "diseases": offlabel_diseases
            }
        
        product['Offlabel'] = {
            "crops": offlabel_crops,
            "diseases": offlabel_diseases
        }
        
        product["minorUse"] = {
            "crops": minorUse_crops,
            "diseases": minorUse_diseases
        }

    # Save the updated JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(godkjente_data, json_file, indent=4, ensure_ascii=False)

    print("The godkjente_plantevernmidler_data.json file has been updated successfully.")
    
if __name__ == "__main__":
    run()