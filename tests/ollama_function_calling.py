import json
import ollama

# Define available functions with descriptions and parameters
functions = [
    {
        "name": "get_weather",
        "description": "Fetches the weather for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The name of the city or location."}
            },
            "required": ["location"]
        }
    },
    {
        "name": "book_flight",
        "description": "Books a flight based on destination and date.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {"type": "string", "description": "The flight's destination city."},
                "date": {"type": "string", "description": "The date of travel in YYYY-MM-DD format."}
            },
            "required": ["destination", "date"]
        }
    }
]

# Simulated function execution
def execute_function(function_name, parameters):
    if function_name == "get_weather":
        location = parameters.get("location")
        return {"result": f"The weather in {location} is sunny and 25°C."}  # Simulate API response
    elif function_name == "book_flight":
        destination = parameters.get("destination")
        date = parameters.get("date")
        return {"result": f"Flight to {destination} on {date} has been booked successfully!"}
    else:
        return {"error": "Unknown function."}

# Function to handle prompt using Ollama
def handle_prompt_with_ollama(prompt, functions):
    # Chat history to maintain context
    chat_history = []

    # Convert function definitions into JSON for Ollama
    function_descriptions = json.dumps(functions)

    # Send prompt to Ollama
    response = ollama.chat(
        model="llama2-chat",  # Replace with your chosen model name
        prompt=prompt,
        history=chat_history,
        functions=function_descriptions
    )

    # Parse Ollama's response to determine function call
    if response.get("function_call"):
        function_name = response["function_call"]["name"]
        parameters = response["function_call"].get("arguments", {})
        # Execute the function with the provided parameters
        return execute_function(function_name, parameters)
    else:
        # No function matched; fallback to regular response
        return {"response": response.get("content", "Sorry, I couldn't process your request.")}

# Simulated chat prompts
chat_prompts = [
    "What's the weather in Paris?",
    "Book a flight to New York tomorrow."
]

# Process each prompt using Ollama
for prompt in chat_prompts:
    print(f"User: {prompt}")
    response = handle_prompt_with_ollama(prompt, functions)
    print(f"AI: {response.get('result', response.get('response'))}")
