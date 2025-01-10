import spacy
import re
import os

class NLPIntentClassifier:

    def __init__(self):
        self.intents = {
            'book': ["book an appointment", "schedule a meeting", "set up an appointment", "reserve a slot"],
            'cancel': ["cancel an appointment", "delete my booking", "remove my meeting", "call off my reservation"],
            'reschedule': ["reschedule my appointment", "change the time", "move my booking", "adjust my schedule", "postpone the meeting"],
        }

        # load NLP pre-trained model
        self.nlp = spacy.load("en_core_web_lg")
        self.threshold = 0.8

    def is_question(self, user_input):
        
        if re.match(r"^(how|what|can|when|where|is|do|does)\b", user_input.lower()) or user_input.endswith("?"):
            return True
        return False
    
    def detect_user_intent(self, user_input):

        if self.is_question(user_input):
            return "Asking a question"
        
        doc = self.nlp(user_input.lower())
        highest_similarity = 0
        detected_intent = "unknown"

        for intent, examples in self.intents.items():
            
            for example in examples:
                example_doc = self.nlp(example)
                similarity = doc.similarity(example_doc)
                if similarity > highest_similarity: 
                    highest_similarity = similarity
                    detected_intent = intent

        if highest_similarity > self.threshold:
            return detected_intent
        
        return "unknown"


def detect_recommendation(query):
    # Keywords for recommendation detection in English and German
    recommendation_keywords = [
        'recommend', 'suggest', 'suitable', 'advise', 'should', 'best', 'guidance', 'advice', 'favor',  # English
        'empfehlen', 'vorschlagen', 'geeignet', 'beraten', 'sollte', 'beste', 'anleitung', 'rat', 'gefälligkeit'  # German
    ]
    
    query_lower = query.lower()
    # Check for any keywords in the query
    if any(re.search(r'\b' + re.escape(word) + r'\b', query_lower) for word in recommendation_keywords):
        return True
    else:
        return None

# Policy type keywords for identification
POLICY_TYPES = {
    "Health Insurance": ["health insurance", "medical coverage", "hospitalization"],
    "Life Insurance": ["life insurance", "beneficiary", "death benefit"],
    "Auto Insurance": ["auto insurance", "vehicle coverage", "car policy"],
    "Home Insurance": ["home insurance", "property coverage", "homeowner policy"],
    "Travel Insurance": ["travel insurance", "trip coverage", "travel protection"],
}


def identify_insurance_policy_type(document_content):
    """
    Identifies the insurance policy type based on keywords in the document content.
    """
    for policy_type, keywords in POLICY_TYPES.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", document_content, re.IGNORECASE):
                return policy_type
    return "Unknown Policy Type"