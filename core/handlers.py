import os
import time
import streamlit as st
from helpers.helpers import set_chat_id
from helpers.greetings_helpers import handle_greeting
from core.stream_handler import StreamHandler
from core.intent_classifier import NLPIntentClassifier
from core.data_masking import SensitiveDataMasker
from services.mongo_db_service import ChatService
from services.geminiai_service import GeminiAIService
from services.openai_service import AzureOpenAIService
from services.mongo_db_service import MongoDBConnectionService

def process_chat_response(ai_response, prompt, data_masker):
    """Handles AI response generation, unmasking, and saving to MongoDB."""
    if ai_response:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for dots in range(5):
                message_placeholder.markdown(f"**Generating{'.' * dots}**")
                time.sleep(0.5)

            # Stream handler (to simulate streaming response)
            stream_handler = StreamHandler(message_placeholder)

            masked_response = ai_response
            
            original_entities = st.session_state['original_entities']
            unmasked_data = data_masker.unmask_text(masked_response, original_entities)
            
            message_placeholder.markdown(unmasked_data)

        st.session_state.messages.append({"role": "assistant", "content": unmasked_data})
        save_chat_to_db(prompt, unmasked_data)

        if st.session_state.current_file_processed:
            st.session_state.file_processed = True
            # st.rerun()

        chat_id = set_chat_id()
        # with st.sidebar:
        #     st.markdown(
        #         f'<div class="cstm-div"><a href="/?chat_id={chat_id}" class="sidebar_text" target="_self">{prompt}</a></div>',
        #         unsafe_allow_html=True
        #     )


def save_chat_to_db(prompt, response):
    """Saves chat and response to MongoDB."""
    chat_id = set_chat_id()
    userId = os.getenv('USER_ID')

    # MongoDB connection setup
    connection = MongoDBConnectionService(uri=os.getenv('MONGODB_URL'), db_name=os.getenv('DB_NAME'))
    connection.connect()
    
    chat_service = ChatService(db_connection=connection)
    chat_service.create_chat({"chatId": chat_id, "userId": userId, "userPrompt": prompt, "response": response}, chat_id)
    

def process_greeting_response(prompt):
    greeting_message = handle_greeting(prompt)
    if greeting_message:
        with st.chat_message("assistant"):
            st.markdown(greeting_message)
        st.session_state.messages.append({"role": "assistant", "content": greeting_message})
        save_chat_to_db(prompt, greeting_message)

        if st.session_state.current_file_processed:
            st.session_state.file_processed = True
            st.rerun()

        return True

    return False


import re

def correct_formatting(text: str) -> str:
    
    # Add a space after periods, question marks, and exclamation marks if missing
    text = re.sub(r'(?<=[.!?])(?=[^\s])', ' ', text)

    # Fix capitalization of the first letter of each sentence
    sentences = re.split(r'([.!?]\s+)', text)  # Split by punctuation followed by space
    text = ''.join(
        sentence.capitalize() if i % 2 == 0 else sentence  # Capitalize the sentence
        for i, sentence in enumerate(sentences)
    )

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def handle_user_input():

    if prompt := st.chat_input("Say something"):
        prompt = correct_formatting(prompt)
        chat_id = set_chat_id()
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        greeting_response = process_greeting_response(prompt)
        if greeting_response:
            return
        
        with st.spinner('Analyzing...'):
            data_masker = SensitiveDataMasker()
            anonymized_data = data_masker.mask_sensitive_data(prompt)
            anonymized_text = anonymized_data['anonymized_text']
            # time.sleep(0.5)
            # return

        nlp_instance = NLPIntentClassifier()
        nlp_intent = nlp_instance.detect_user_intent(prompt)

        if os.getenv('AI_USED') == 'AZURE OPEN AI':
            openai_client = AzureOpenAIService()
            azure_ai_response = openai_client.generate_response(anonymized_text)
            process_chat_response(azure_ai_response, prompt, data_masker)

        elif os.getenv('AI_USED') == 'GEMINI':
            try:
                gemini_service = GeminiAIService()
                gemini_ai_response = gemini_service.generate_response(anonymized_text)
                process_chat_response(gemini_ai_response, prompt, data_masker)
            except ValueError as ve:
                st.error(ve)

        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                for dots in range(5):
                    message_placeholder.markdown(f"**Generating{'.' * dots}**")
                    time.sleep(0.5)

                stream_handler = StreamHandler(message_placeholder)

                masked_response = st.session_state.conversation.predict(input=anonymized_text, callbacks=[stream_handler])
                
                original_entities = st.session_state['original_entities']
                
                unmasked_data = data_masker.unmask_text(masked_response, original_entities)
                message_placeholder.markdown(unmasked_data)

            st.session_state.messages.append({"role": "assistant", "content": unmasked_data})
            save_chat_to_db(prompt, unmasked_data)

            with st.sidebar:
                st.markdown(
                    f'<div class="cstm-div"><a href="/?chat_id={chat_id}" class="sidebar_text" target="_self">{prompt}</a></div>',
                    unsafe_allow_html=True
                )
