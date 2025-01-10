
import os
import pandas as pd
import streamlit as st
import google.generativeai as genai
from services.chromadb_service import *
from core.intent_classifier import detect_recommendation
from core.intent_classifier import identify_insurance_policy_type
from langdetect import detect

chat_history = []

class GeminiAIService:
    def __init__(self):
        # Initialize API key and model configuration
        self.api_key = os.getenv('GEMINI_AI_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required to use the GeminiAIService.")

        self.model_name = os.getenv('GEMINI_AI_MODEL', "gemini-2.0-flash-exp")
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        # Configure the genai API and initialize the model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )

    def generate_embeddings(self, content, chunk_size=3000):
        """
        Generate embeddings for the given content using the Gemini AI API.
        """
        try:
            # Split the content into smaller chunks
            chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
            embeddings = []

            for chunk in chunks:
                result = genai.embed_content(model="models/text-embedding-004", content=chunk)
                chunk_embedding = result.get("embedding", [])

                # Ensure the embedding is a list of floats
                if isinstance(chunk_embedding, list):
                    chunk_embedding = [float(value) for value in chunk_embedding]
                    embeddings.append(chunk_embedding)
                else:
                    raise ValueError("Embedding is not in a valid format.")

            # Combine embeddings (e.g., averaging them)
            final_embedding = [
                sum(values) / len(values) for values in zip(*embeddings)
            ]

            return final_embedding

        except Exception as e:
            st.error(f"Error generating embedding: {e}")
            return []


    def build_prompt(self, prompt, document_content, intent, context):

        if document_content:
            document_content = document_content
     
        else:
            document_content = document_content
    
        # Detect the language of the prompt
        language = detect(prompt)

        # Define templates for both languages
        english_template = """
            Based on the document content:
            {document_content}

            Detect the user's current insurance policy details and profile, including:
            - Policy Type
            - Premium
            - Coverage
            - User Profile (Age, Location, Health Conditions)

            Recommend 3 to 5 insurance policies that meet these criteria:
            1. Match or exceed the user's current coverage.
            2. Offer a lower or comparable premium.
            3. Are available in the user's location.

            **Instructions:**
            - Detect the current insurance policy details and user profile automatically from the provided context.
            - Summarize the user's data in 1-2 sentences.
            - Follow this format for each recommendation:
            
            1. **Provider Name**: Provider Name
                - **Policy Type**: Policy Type
                - **Coverage Amount**: Coverage Amount
                - **Premium**: Premium
                - **Why This Policy is Recommended**: Reason for recommendation

            ***Conclude with a brief summary of why these policies are suitable based on the user's profile, highlighting key benefits or features.***
        """

        german_template = """
            Basierend auf dem Dokumentinhalt:
            {document_content}

            Erkennen Sie die aktuellen Versicherungsdetails und das Profil des Nutzers, einschließlich:
            - Policentyp
            - Prämie
            - Deckung
            - Benutzerprofil (Alter, Standort, Gesundheitszustand)

            Empfehlen Sie 3 bis 5 Versicherungspolicen, die folgende Kriterien erfüllen:
            1. Entsprechen oder übertreffen die aktuelle Deckung des Nutzers.
            2. Bieten eine niedrigere oder vergleichbare Prämie.
            3. Sind im Standort des Nutzers verfügbar.

            **Anweisungen:**
            - Erkennen Sie automatisch die aktuellen Versicherungsdetails und das Benutzerprofil aus dem bereitgestellten Kontext.
            - Fassen Sie die Daten des Nutzers in 1-2 Sätzen zusammen.
            - Verwenden Sie für jede Empfehlung dieses Format:
            
            1. **Anbietername**: Anbietername
                - **Policentyp**: Policentyp
                - **Deckungssumme**: Deckungssumme
                - **Prämie**: Prämie
                - **Warum diese Police empfohlen wird**: Grund der Empfehlung

            ***Schließen Sie mit einer kurzen Zusammenfassung ab, warum diese Policen auf das Profil des Nutzers abgestimmt sind und welche Vorteile oder Merkmale besonders hervorzuheben sind.***
        """

        if document_content and intent:
            
            if language == 'de':  # German
                return german_template.format(document_content=document_content)
            else: 
                return english_template.format(document_content=document_content)
            
        elif document_content:
            return f"Context: {document_content}\n\nQuestion: {prompt}\n\nAnswer based on the context:"
        
        else:
            return f"You are an informative and friendly assistant. Provide detailed and specific answers to user queries in short summery. Queries: {prompt}"

    def generate_response(self, prompt):
        """
        Generate a response based on the user query and relevant documents.
        """        
        try:
            # Retrieve document content from session state
            document_content = st.session_state.get("document_content", "")

            # Generate query embeddings
            # query_embeddings = self.generate_embeddings(prompt)

            # Identify policy type
            # policy_type = identify_insurance_policy_type(prompt)

            # Retrieve matching documents and extract metadata
            # response = retrieve_matching_documents(query_embeddings, policy_type)
            
            # Check if response is not empty and extract relevant information
            # if response:
            
            #     metadata = response[0].get('metadata', [])
            #     context = response[0].get('content', [])
            # else:
            #     metadata = None
            context = None

            # Display metadata in the UI
            # st.subheader("Source Files")
            # st.table(pd.DataFrame(metadata))

            # Detect user intent
            intent = detect_recommendation(prompt)
            
            # Build the appropriate prompt
            full_prompt = self.build_prompt(prompt, document_content, intent, context)

            # Start a chat with the model
            chat = self.model.start_chat(history=chat_history)

            # Generate the response
            with st.spinner('Generating...'):
                response = chat.send_message(full_prompt)

            # Update chat history
            chat_history.append({"role": "user", "parts": full_prompt})
            chat_history.append({"role": "model", "parts": response.text})

            return response.text

        except Exception as e:
            return f"An error occurred while generating a response: {e}"


