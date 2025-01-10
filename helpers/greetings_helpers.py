import random
import json
import os

DATASET_FOLDER = "dataset"
GREETINGS_FILE_PATH = os.path.join(DATASET_FOLDER, "greetings.json")

def load_greetings():
    try:
        with open(GREETINGS_FILE_PATH, "r") as file:
            data = json.load(file)
            return data.get("greetings", [])
    except FileNotFoundError:
        print(f"Error: The file '{GREETINGS_FILE_PATH}' was not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the greetings file.")
        return []

def handle_greeting(user_input):

    greetings_triggers = ["hi", "hello", "hey", "greetings", "howdy", "hola"]
    user_greeting = user_input.lower().strip()
    
    if user_greeting in greetings_triggers:
        greetings = load_greetings()
        if greetings:
            return random.choice(greetings)
        else:
            return "Error: Unable to load greetings."
    else:
        return None
