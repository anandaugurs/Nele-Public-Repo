import random

# Define responses and prompts
greetings = ["hello", "hi", "hey", "hola", "greetings"]
questions = [
    "How can I help you today?",
    "What can I assist you with?",
]

responses = {
    "how are you": "I'm just a bot, but I'm doing fine! How about you?",
    "bye": "Goodbye! Have a great day!",
}


appointment_details = []


def get_bot_response(user_input):
    user_input = user_input.lower().strip()

    if any(greeting in user_input for greeting in greetings):
        return "Hello! Would you like to book an appointment?"
    
    elif user_input in responses:
        return responses[user_input]
    
    elif "yes" in user_input or "appointment" in user_input:
        return "Sure! I will help you book an appointment. Please provide the following details."

    else:
        return "Sorry, I didn't quite understand that. " + random.choice(questions)

def book_appointment():
    global appointment_details

    print("Bot: Let's get started with booking your appointment.")
    
    name = input("Bot: What's your name? ")
    appointment_details.append(('Name', name))

    date = input("Bot: When would you like to schedule the appointment? (Please provide a date in MM/DD/YYYY format) ")
    appointment_details.append(('Date', date))

    time = input("Bot: What time would you prefer for the appointment? (Please provide time in HH:MM format) ")
    appointment_details.append(('Time', time))

    reason = input("Bot: What is the reason for the appointment? ")
    appointment_details.append(('Reason', reason))

    print("\nBot: Here are your appointment details:")
    for detail in appointment_details:
        print(f"{detail[0]}: {detail[1]}")
    
    confirmation = input("\nBot: Does everything look good? (yes/no) ")
    if confirmation.lower() == "yes":
        print("Bot: Your appointment has been successfully booked!")
    else:
        print("Bot: Please restart the process to update your appointment details.")
    
# Main chatbot loop
def chatbot():
    print("Bot: Hello! How can I assist you today? (Type 'bye' to exit)")
    
    while True:
        user_input = input("You: ")

        if user_input.lower() == "bye":
            print("Bot: Goodbye! Have a great day!")
            break

        bot_response = get_bot_response(user_input)
        print(f"Bot: {bot_response}")
        
        if "yes" in user_input or "appointment" in user_input:
            book_appointment()
            break 

# Run the chatbot
if __name__ == "__main__":
    chatbot()
