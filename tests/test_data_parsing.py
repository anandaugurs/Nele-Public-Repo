import spacy
import re
from langdetect import detect

nlp_models = {
    "en": spacy.load("en_core_web_lg"),
    "de": spacy.load("de_core_news_sm"),
}

def parse_insurance_document(document_text):
   
    # Step 1: Detect document language
    try:
        language = detect(document_text)
    except Exception as e:
        print("Language detection failed:", e)
        return {"error": "Language detection failed"}

    print(f"Detected Language: {language.upper()}")

    # Step 2: Load appropriate SpaCy model
    nlp = nlp_models.get(language, nlp_models["en"])  # Default to English

    # Step 3: Define regex patterns for English and German
    patterns = {
        "en": {
            "premium": r"Premium:\s?\$?(\d+)",
            "coverage": r"Coverage:\s?(.*?)(?=\n)",
            "exclusions": r"Exclusions:\s?(.*?)(?=\n)",
        },
        "de": {
            "premium": r"Prämie:\s?\€?(\d+)",
            "coverage": r"Deckung:\s?(.*?)(?=\n)",
            "exclusions": r"Ausschlüsse:\s?(.*?)(?=\n)",
        },
    }
    selected_patterns = patterns.get(language, patterns["en"])

    # Step 4: Extract features using regex
    premium = re.search(selected_patterns["premium"], document_text)
    coverage = re.search(selected_patterns["coverage"], document_text)
    exclusions = re.search(selected_patterns["exclusions"], document_text)

    # NLP for named entity recognition (NER)
    doc = nlp(document_text)

    # Step 5: Return extracted information
    features = {
        "language": language,
        "premium": float(premium.group(1)) if premium else None,
        "coverage": coverage.group(1).strip() if coverage else None,
        "exclusions": exclusions.group(1).strip() if exclusions else None,
        "key_terms": [ent.text for ent in doc.ents if ent.label_ in ["ORG", "MONEY", "GPE"]],
    }

    return features


# Example insurance documents in English and German
insurance_document_en = """
Policy Name: Health Plus Plan
Coverage: Covers hospitalization, surgery, and critical illness
Premium: $200
Exclusions: Pre-existing diseases, cosmetic surgery
Provider: ABC Insurance Corp
"""

insurance_document_de = """
Versicherungsname: Gesundheits-Plus-Plan
Deckung: Deckt Krankenhausaufenthalte, Operationen und kritische Krankheiten ab
Prämie: €200
Ausschlüsse: Vorerkrankungen, kosmetische Operationen
Anbieter: ABC Versicherung AG
"""

# Parse English document
parsed_features_en = parse_insurance_document(insurance_document_en)
print("Extracted Features:", parsed_features_en)

# Parse German document
parsed_features_de = parse_insurance_document(insurance_document_de)
print("Extracted Features:", parsed_features_de)
