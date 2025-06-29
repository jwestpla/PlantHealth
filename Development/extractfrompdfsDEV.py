import re
import fitz
import os
import sys
from collections import OrderedDict

# Make crops_diseases importable from one folder above
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crops_diseases import crops, diseases

def run():
    """
    Extract relevant information from specific PDF files for crop and disease detection.
    Writes results to 'extracted_sentencesDEV.txt'.
    """

    def extract_text_from_pdf(pdf_path):
        text = ""
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text")
        print(text)
        return text

    def extract_first_sentence_after_section(text):
        patterns = [
            r'\b(Bruksområde|BRUKSOMRÅDE)\s*:?',
            r'\b(Bruksrettledning|BRUKSRETTLEDNING)\b\s*:?',
            r'\b(Betingelser for bruk|BETINGELSER FOR BRUK)\b\s*:?',
            r'\b(Bruks- og virkeområde|BRUKS- OG VIRKEOMRÅDE)\b\s*:?',
            r'\b(Bruksområde og virkeområde|BRUKSOMRÅDE OG VIRKEOMRÅDE)\b\s*:?',
            r'\b(Dosering|DOSERING)\b\s*:?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                start_pos = match.end()
                following_text = text[start_pos:].strip()
                first_sentence_match = re.match(r'^([^.!?]*\([^)]*\))*[^.!?]*[.!?]', following_text)
                if first_sentence_match:
                    return first_sentence_match.group().strip()
                break
        return "Not found"

    def extract_text_after_virkeomrade(text):
        # Match start of the section
        match = re.search(
            r'\b(Virkeområde og virkemåte|VIRKEOMRÅDE OG VIRKEMÅTE|Virkeområde|VIRKEOMRÅDE|Virkning|VIRKNING)\s*:?', 
            text
        )
        if match:
            start_pos = match.end()
            following_text = text[start_pos:].strip()

            # Match end of the section
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

    # Hardcoded list of specific files to test
    test_files = ['2018.2.pdf', "2023.19.pdf"]

    pdf_directory = os.path.join(os.path.dirname(__file__), 'test_labels')
    output_file_path = os.path.join(os.path.dirname(__file__), 'extracted_sentencesDEV.txt')

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for filename in test_files:
            pdf_path = os.path.join(pdf_directory, filename)
            if os.path.exists(pdf_path):
                try:
                    text = extract_text_from_pdf(pdf_path)

                    # Extract first section (Bruksområde etc.)
                    first_sentence = extract_first_sentence_after_section(text)
                    found_crops = extract_crops_from_sentance(first_sentence, crops)
                    found_diseases_from_crops_section = extract_diseases_from_paragraph(first_sentence, diseases)

                    # Extract second section (Virkeområde etc.)
                    first_sentance_disease = extract_text_after_virkeomrade(text)
                    found_diseases = extract_diseases_from_paragraph(first_sentance_disease, diseases)

                    # Combine disease lists (remove duplicates, preserve order)
                    combined_diseases = list(OrderedDict.fromkeys(found_diseases + found_diseases_from_crops_section))

                    output_file.write(f"File: {filename}\n")
                    output_file.write(f"First Sentence: {first_sentence}\n")
                    output_file.write(f"Crops: {found_crops}\n")
                    output_file.write(f"Diseases paragraph: {first_sentance_disease}\n")
                    output_file.write(f"Diseases: {combined_diseases}\n\n")

                except Exception as e:
                    output_file.write(f"Error processing file {filename}: {e}\n\n")
            else:
                output_file.write(f"File {filename} not found in {pdf_directory}\n\n")

    print(f"Sentence extraction completed. Results saved to {output_file_path}")

if __name__ == "__main__":
    run()