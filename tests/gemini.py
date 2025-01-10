import google.generativeai as genai
import os

API_KEY = "AIzaSyCw-wgjlTqLy-B1f31-2JSsZS1g2ZKh-j8" 
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

def generate_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text  
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example Usage
if __name__ == "__main__":
    user_prompt = "Explain the concept of Quantum Computing in simple terms."
    result = generate_gemini_response(user_prompt)
    if result:
        print("Response from Gemini 2.0 Flash:")
        print(result)
