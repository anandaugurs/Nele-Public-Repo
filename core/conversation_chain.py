from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from services.ollama_service import OllamaService
from langchain_community.llms import Ollama
import streamlit as st
import os

backup_templates = """The following is a friendly conversation between a human and an AI. 
        The AI is talkative, provides lots of specific details from its context, and avoids repeating itself unnecessarily. 
        If the AI does not know the answer to a question, it truthfully says it does not know. AI should not return human and AI conversation in the response

        If the human asks something that requires a specific function (like checking the booking an appointment), the AI should specify the function name 
        and the required parameters in the following format:
     
        Function Call: {{ "name": "<function_name>", "parameters": <parameters_in_json_format> }}

        Here are the function names the AI can use:
        1. book_appointment

        Current conversation:
        {history}
        Human: {input}
        AI: """



def initialize_conversation_chain():
    """Initializes the conversation chain for generating AI responses."""
    template = """The following is a friendly conversation between a human and an AI. 
        The AI is talkative, provides lots of specific details from its context, and avoids repeating itself unnecessarily. 
        If the AI does not know the answer to a question, it truthfully says it does not know. AI should not return human and AI conversation in the response

        Current conversation:
        {history}
        Human: {input}
        AI: """

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
    ollama_service = OllamaService()
    llm = ollama_service.initialize_llm()

    if "conversation" not in st.session_state:
     
        st.session_state.conversation = ConversationChain(
            llm=llm,
            verbose=True,
            memory=ConversationBufferMemory(human_prefix="Human", ai_prefix="AI"),
            prompt=PROMPT
        )
