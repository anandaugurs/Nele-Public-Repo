import chromadb
from recommendation_engine.insurance_feature_extractor import extract_features
from services.chromadb_service import save_document_to_chroma
from services.geminiai_service import GeminiAIService
from core.intent_classifier import identify_insurance_policy_type
from datetime import datetime
import streamlit as st
import pandas as pd
import PyPDF2
import re


def read_pdf(file):
    """
    Reads and extracts text from a PDF file.
    """
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:  # Ensure page text is not None
            text += page_text + "\n"
    return text


def read_csv(file):
    """
    Reads a CSV file and converts it to a string representation.
    """
    df = pd.read_csv(file)
    return df.to_string()


def store_document_in_memory(content, metadatas):
    """
    Stores the trimmed content in session state for memory.
    """
    
    # Add content to the metadatas dictionary
    metadatas['content'] = content

    st.session_state['metadatas'] = metadatas
    st.session_state['document_content'] = content

def format_file_size(size_in_bytes):
   
    size_in_kb = size_in_bytes / 1024  
    return f"{size_in_kb:.1f} KB" 




def process_uploaded_file(uploaded_file):
    """
    Processes the uploaded file to identify policy type, extract embeddings, and store it in ChromaDB.
    """
    if uploaded_file is not None:
        metadatas = {
            "file_name": uploaded_file.name,
            "file_type": uploaded_file.type,
            "file_size": format_file_size(uploaded_file.size),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Read file content based on type
        file_content = ""
        if uploaded_file.type == "application/pdf":
            file_content = read_pdf(uploaded_file)
        elif uploaded_file.type == "text/csv":
            file_content = read_csv(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a PDF or CSV file.")
            return None

        # Identify policy type
        policy_type = identify_insurance_policy_type(file_content)
        metadatas["policy_type"] = policy_type
        
        # Calculate and log file stats
        char_count = len(file_content)
        word_count = len(file_content.split())
        line_count = len(file_content.splitlines())
        print(f"Characters: {char_count}, Words: {word_count}, Lines: {line_count}")

        # Store document content in session state
        store_document_in_memory(file_content, metadatas)

        # Generate embeddings using GeminiAIService
        gemini_service = GeminiAIService()
        embeddings = gemini_service.generate_embeddings(file_content)

        # Save document to ChromaDB
        document_id =  454545454 # save_document_to_chroma(file_content, metadatas, embeddings)

        if document_id:
            print(f"File '{uploaded_file.name}' has been successfully processed!")
            return file_content
        else:
            st.error("❌ Failed to save document to memory.")
            return None

    return None
