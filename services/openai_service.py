import requests
import os
import streamlit as st

class AzureOpenAIService:
    
    def __init__(self, api_key=None):
       
        self.api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = f"https://neleaitest.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

    def generate_response(self, conversation_input):

        document_content = st.session_state.get("document_content", "")

        if not document_content:
            system_message = "You are an informative and friendly assistant. Provide detailed and specific answers to user queries."
        
        else:
            system_message = f"""
            You are an informative and friendly assistant. You have access to the following document content:
            {document_content}
            
            Please answer the following query based on the document content.
            """
        
        payload = { 
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": conversation_input}
            ],
            "temperature": 0.7, 
            "top_p": 0.9, 
            "max_tokens": 50
        }
        
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            return ai_response

        except requests.RequestException as e:
            print(f"Failed to make the request. Error: {e}")
            return None
        except ValueError:
            print("Failed to decode the JSON response.")
            return None
