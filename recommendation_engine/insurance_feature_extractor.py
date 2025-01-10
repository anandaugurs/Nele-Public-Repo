import pdfplumber
import re

# Define a dictionary for field mapping including English and German field names
FIELD_MAPPING = {
    "Policy Type": ["Policy Type", "Type of Policy", "Plan Type", "Versicherungsart", "Art der Versicherung"],
    "Coverage": ["Coverage", "Coverage Amount", "Sum Insured", "Insured Value", "Deckung", "Versicherte Summe", "Versicherungssumme"],
    "Premium": ["Premium", "Premium Amount", "Total Premium", "Payment Due", "Prämie", "Versicherungsbeitrag"],
    "Insured Name": ["Policyholder Name", "Name of Policyholder", "Insured Name", "Name des Versicherungsnehmers", "Versicherungsnehmer", "Name"],
    "Age": ["Policyholder Age", "Age of Policyholder", "Insured Age", "Alter des Versicherungsnehmers", "Versicherungsalter", "Age"],
    "Location": ["Policyholder Location", "Address", "Insured Location", "Standort des Versicherungsnehmers", "Adresse", "Location"]
}

def clean_extracted_value(value):
    """
    Clean the extracted value by removing leading and trailing unwanted characters.
    """
    if isinstance(value, str):
        cleaned_value = value.strip(" :.-").strip()
        return cleaned_value
    return value

def extract_features(text):
    """
    Extract all required fields from the text.
    """
    extracted_data = {}
    
    for field, field_names in FIELD_MAPPING.items():
        field_found = False 
        for field_name in field_names:

            pattern = rf"(?:\b{field_name}\b\s*[:-]?\s*)(.+)"
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:

                for match in matches:
                    cleaned_value = clean_extracted_value(match)
                    if cleaned_value: 
                        extracted_data[field] = cleaned_value
                        field_found = True
                        break
            if field_found:
                break

        # If no match found, set default value
        if field not in extracted_data:
            extracted_data[field] = "Not Found"

    return extracted_data

