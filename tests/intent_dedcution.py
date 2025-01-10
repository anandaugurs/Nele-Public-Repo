def detect_user_intent(user_input):
  
    intents = {
        'book': ["book", "schedule", "set up", "make an appointment", "reserve"],
        'cancel': ["cancel", "delete", "remove", "drop", "call off"],
        'reschedule': ["reschedule", "change", "move", "adjust", "postpone", "shift"]
    }

    user_input = user_input.lower()

    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input:
                return intent

    # If no match is found, return 'unknown'
    return "unknown"


import spacy

# Load a pre-trained NLP model
nlp = spacy.load("en_core_web_lg")

def get_intent(user_input):
    doc = nlp(user_input.lower())
    
    # Define patterns or rules for each intent
    if "book" in doc.text or "schedule" in doc.text:
        return "book"
    elif "cancel" in doc.text or "delete" in doc.text:
        return "cancel"
    elif "reschedule" in doc.text or "change" in doc.text:
        return "reschedule"
    else:
        return "unknown"

# Example usage




# Example usage
if __name__ == "__main__":
    user_input = "Can you help me cancel my appointment?"
    user_queries = [
        "I want to book an appointment for next week.",
        "Can you cancel my meeting?",
        "I need to reschedule the appointment to tomorrow.",
        "What's the weather like?"
    ]

    for query in user_queries:
        intent = detect_user_intent(query)
        nlp_intent = get_intent(query)
        print("NLP User Intent:", nlp_intent)
        print(f"User Query: '{query}' => Detected Intent: '{intent}'")
