import spacy
import re
from langdetect import detect
import streamlit as st
# Load SpaCy NLP models for English and German

nlp_models = {
    "en": spacy.load("en_core_web_lg"),
    "de": spacy.load("de_core_news_sm"),
}

def parse_insurance_document(document_text):
    try:
        language = detect(document_text)
    except Exception as e:
        return {"error": f"Language detection failed: {e}"}

    nlp = nlp_models.get(language, nlp_models["en"])  # Default to English
 
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

    premium = re.search(selected_patterns["premium"], document_text)
    coverage = re.search(selected_patterns["coverage"], document_text)
    exclusions = re.search(selected_patterns["exclusions"], document_text)

    # st.info(f"Language: {language}, Premium: {premium} Coverage: {coverage} Exclusings: {exclusions}")

    # NLP for named entity recognition (NER)
    doc = nlp(document_text)

    features = {
        "language": language,
        "premium": float(premium.group(1)) if premium else None,
        "coverage": coverage.group(1).strip() if coverage else None,
        "exclusions": exclusions.group(1).strip() if exclusions else None,
        "key_terms": [ent.text for ent in doc.ents if ent.label_ in ["ORG", "MONEY", "GPE"]],
    }
    st.info(features)
    return features
