import random

# List of greeting messages
greetings = [
    "Hi! I’m here to assist you in finding the perfect insurance policy for your needs. How can I help today?",
    "Hello! Ready to help you find the best insurance plan. What can I do for you?",
    "Hey there! Let’s explore the best insurance options for you.",
    "Greetings! I'm here to guide you through selecting the right insurance policy.",
    "Good day! I'm excited to help you find the best insurance solution.",
    "Welcome! I’m your personal guide to finding the best insurance policy tailored to you.",
    "Hi! I’m here to help you choose the right insurance plan. Let’s get started!",
    "Hello there! Need help finding an insurance policy? I’m here to assist you!",
    "Hey! Looking for an insurance plan? I can help you with that.",
    "Hi! Let’s get you the best insurance coverage. How can I assist you today?"
]

def handle_greeting(user_input):
    greetings_triggers = ["hi", "hello", "hey", "greetings", "howdy", "hola"]
    user_greeting = user_input.lower().strip()

    # Check if the user's input matches a greeting trigger
    if user_greeting in greetings_triggers:
        # Return a random greeting message from the list
        return random.choice(greetings)
    else:
        return "How can I help you today?"


user_input = input()
print(handle_greeting(user_input))  
