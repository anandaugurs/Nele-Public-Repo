from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer import AnalyzerEngine
from langdetect import detect
import streamlit as st
import re

class SensitiveDataMasker:
 
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "de", "model_name": "de_core_news_sm"},
                {"lang_code": "en", "model_name": "en_core_web_lg"},
            ],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        self.nlp_engine = provider.create_engine()
        self.analyzer = AnalyzerEngine(nlp_engine=self.nlp_engine, supported_languages=["en", "de"])
   
    def mask_sensitive_data(self, text: str) -> dict:
        """
        Masks sensitive data in the provided text for the specified language.
        """
        language = 'en'
        
        # Analyze text for sensitive entities
        analysis_results = self._analyze_text(text, language)
       
        # Anonymize the text
        anonymized_results = self._anonymize_text(text, analysis_results)

        # Extract anonymized text and entities
        anonymized_text = anonymized_results.text
        anonymized_entities = anonymized_results.items

        return {
            "original_text": text,
            "language": language,
            "anonymized_text": anonymized_text,
            "anonymized_entities": anonymized_entities,
        }
    
    def _analyze_text(self, text: str, language: str):
        """
        Analyzes the text to extract sensitive entities for the specified language.
        """
        analysis_results = self.analyzer.analyze(text=text, language=language)

        # Extract original entities for reference
        original_entities = self._extract_original_entities(text, analysis_results)

        return analysis_results

    def _extract_original_entities(self, text: str, analysis_results: object):
        """
        Extracts original values along with masked values.
        """
        original_entities = []

        for result in analysis_results:
            result_dict = result.to_dict()
            original_entities.append({
                f"<{result.entity_type}>": text[result.start:result.end],
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "original_value": text[result.start:result.end],
                "score": getattr(result, "score", None),
            })

        # Initialize original entities in session state
        if 'original_entities' not in st.session_state:
            st.session_state['original_entities'] = original_entities

        return original_entities

    def _anonymize_text(self, text: str, analysis_results: object):
        """
        Anonymizes the text based on the analysis results.
        """
        return self.anonymizer.anonymize(text=text, analyzer_results=analysis_results)

    def unmask_text(self, ai_response: str, original_entities) -> str:
        """
        Reverts the masking of sensitive data.
        """
        unmasked_text = ai_response  

        for item in original_entities:
            entity_type = item.get('entity_type')
            original_value = item.get('original_value')

            if entity_type and original_value:
                # pattern = rf"<{re.escape(entity_type)}>|{re.escape(entity_type)}"
                pattern = rf"<{re.escape(entity_type)}>"
                unmasked_text = re.sub(pattern, original_value, unmasked_text, count=1, flags=re.IGNORECASE)
        return unmasked_text

