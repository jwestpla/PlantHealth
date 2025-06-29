import re
import fitz
import os
from collections import OrderedDict
from crops_diseases import crops, diseases

def run():
    """
    * Construct functions to extract text from pdf to string, and to look for crops and diseases using RegEx
    in the relevant sections of the pdf (most important algorithm of the project)
    * Creates a new document, called "Extracted_sentences" where each product id is saved, as well as the string
    for finding crops and diseases. This is used for adding crops and diseases, as well as troubleshoot
    * Saves all this information for the final file to update the JSON file
    """

    def extract_text_from_pdf(pdf_path):
        text = ""
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text")
        return text

    def extract_first_sentence_after_section(text):
        match = re.search(r'\b(Bruksområde|BRUKSOMRÅDE)\s*:?', text)

        if not match:
            match = re.search(r'\b(Bruksrettledning|BRUKSRETTLEDNING)\s*:?', text)

        if not match:
            match = re.search(r'\b(Betingelser for bruk|BETINGELSER FOR BRUK)\s*:?', text)

        if not match:
            match = re.search(r'\b(Bruks- og virkeområde|BRUKS- OG VIRKEOMRÅDE)\s*:?', text)

        if not match:
            match = re.search(r'\b(Bruksområde og virkeområde|BRUKSOMRÅDE OG VIRKEOMRÅDE)\s*:?', text)

        if not match:
            match = re.search(r'\b(Dosering|DOSERING)\s*:?', text)

        if match:
            start_pos = match.end()
            following_text = text[start_pos:].strip()
            first_sentence_match = re.match(r'^([^.!?]*\([^)]*\))*[^.!?]*[.!?]', following_text)
            if first_sentence_match:
                return first_sentence_match.group().strip()

        return "Not found"

    def extract_text_after_virkeomrade(text):
        match = re.search(
            r'\b(Virkeområde og virkemåte|VIRKEOMRÅDE OG VIRKEMÅTE|Virkeområde|VIRKEOMRÅDE|Virkning|VIRKNING)\s*:?',
            text
        )
        if match:
            start_pos = match.end()
            following_text = text[start_pos:].strip()

            virkemate_match = re.search(
                r'\b(Virkemåte|VIRKEMÅTE|Virkemåde|VIRKEMÅDE|Virkningsmåte|VIRKNINGSMÅTE)\b',
                following_text
            )
            if virkemate_match:
                return following_text[:virkemate_match.start()].strip()
            else:
                first_sentence_match = re.match(r'^([^.!?]*\([^)]*\))*[^.!?]*[.!?]', following_text)
                if first_sentence_match:
                    return first_sentence_match.group().strip()
        return "Not found"

    def extract_crops_from_sentance(sentence, crops):
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

    pdf_directory = 'final_labels'
    output_file_path = 'extracted_sentences.txt'

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for filename in os.listdir(pdf_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_directory, filename)
                try:
                    text = extract_text_from_pdf(pdf_path)
                    first_sentence = extract_first_sentence_after_section(text)
                    found_crops = extract_crops_from_sentance(first_sentence, crops)
                    diseases_from_bruksomrade = extract_diseases_from_paragraph(first_sentence, diseases)
                    first_sentance_disease = extract_text_after_virkeomrade(text)
                    diseases_from_virkeomrade = extract_diseases_from_paragraph(first_sentance_disease, diseases)

                    combined_diseases = list(OrderedDict.fromkeys(diseases_from_virkeomrade + diseases_from_bruksomrade))

                    if first_sentence:
                        output_file.write(f"File: {filename}\n")
                        output_file.write(f"First Sentence: {first_sentence}\n")
                        output_file.write(f"Crops: {found_crops}\n")
                        output_file.write(f"Diseases paragraph: {first_sentance_disease}\n")
                        output_file.write(f"Diseases: {combined_diseases}\n\n")
                    else:
                        output_file.write(f"File: {filename}\n")
                        output_file.write(f"First Sentence: None found\n\n")
                except Exception as e:
                    output_file.write(f"Error processing file {filename}: {e}\n\n")

    print(f"Sentence extraction completed. Results saved to {output_file_path}")

if __name__ == "__main__":
    run()