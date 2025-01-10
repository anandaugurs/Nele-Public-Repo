import streamlit as st
from typing import List
import uuid

class DocumentManager:
    def __init__(self):
        if 'documents' not in st.session_state:
            st.session_state.documents = {}
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def upload_document(self, uploaded_file) -> str:
        """
        Handle document upload and return document ID
        """
        if uploaded_file is not None:
            # Generate unique ID for the document
            doc_id = str(uuid.uuid4())
            
            # Store document with its metadata
            st.session_state.documents[doc_id] = {
                'name': uploaded_file.name,
                'content': uploaded_file.read(),
                'timestamp': st.session_state.get('timestamp', 0)
            }
            return doc_id
        return None

    def get_document(self, doc_id: str):
        """
        Retrieve document by ID
        """
        return st.session_state.documents.get(doc_id)

    def list_documents(self) -> List[dict]:
        """
        Return list of all uploaded documents
        """
        return [
            {'id': doc_id, 'name': doc['name']}
            for doc_id, doc in st.session_state.documents.items()
        ]

def main():
    st.title("Multi-Document Chat Assistant")
    
    # Initialize document manager
    doc_manager = DocumentManager()
    
    # File uploader in sidebar
    with st.sidebar:
        st.header("Document Upload")
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["txt", "pdf", "doc"],
            key=f"uploader_{len(st.session_state.documents)}"
        )
        
        if uploaded_file:
            doc_id = doc_manager.upload_document(uploaded_file)
            if doc_id:
                st.success(f"Uploaded: {uploaded_file.name}")
        
        # Display list of uploaded documents
        st.header("Uploaded Documents")
        for doc in doc_manager.list_documents():
            st.text(f"📄 {doc['name']}")
    
    # Chat interface
    st.header("Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Here you would process the query against all uploaded documents
        # Add your document processing and AI response logic here
        
        # Example response
        response = f"Processing query: {prompt}\nAgainst {len(st.session_state.documents)} documents"
        
        # Add assistant message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)

if __name__ == "__main__":
    main()
