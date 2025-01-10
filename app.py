import streamlit as st
import os
import base64
from core.conversation_chain import initialize_conversation_chain
from core.file_processing import process_uploaded_file
from core.handlers import handle_user_input
from core.chat_management import ChatManagement
from services.chromadb_service import reset_chroma_db
from services.mongo_db_service import MongoDBConnectionService
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title='Nele.ai - Secure artificial intelligence', layout="wide", page_icon='./static/image/logo.jpeg', initial_sidebar_state='auto')

# Load custom CSS
with open('./static/css/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# JavaScript for custom behavior
components.html(
    """
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const buttons = window.parent.document.querySelectorAll('.stFileUploader button');
            const closed_sidebar_button = window.parent.document.querySelectorAll('.stSidebar .st-emotion-cache-1tokvoz');
            const open_sidebar_button = window.parent.document.querySelectorAll('.st-emotion-cache-19ee8pt');

            if (buttons.length > 0) {
                buttons[0].textContent = 'Browse file'; 
            }

            // Add a simple tooltip using the title attribute
            if (closed_sidebar_button.length > 0) {
                closed_sidebar_button[0].setAttribute('title', 'Close sidebar');
            }
            if (open_sidebar_button.length > 0) {
                open_sidebar_button[0].setAttribute('title', 'Open sidebar');
            }
        });
    </script>
    """,
    height=0,
)

@st.dialog("Delete Chat")
def DeleteChatPopup(chatId):
    st.write("Are you sure you want to delete?")
    if st.button("Yes"):
        # Clear session state and delete chat
        st.session_state.messages.clear()
        st.session_state.file_processed = False
        st.session_state.current_file_processed = False
        st.session_state.document_content_name = None
        st.session_state["messages"] = []
        st.session_state.show_dialog = False

        chat_manager = ChatManagement()
        chat_manager.delete_all_chats(chatId)

        # Remove query parameter
        if "chat_id" in st.query_params:
            del st.query_params["chat_id"]
        st.rerun()
        
def main():
    # mongo_service = MongoDBConnectionService(uri=os.getenv('MONGODB_URL'), db_name=os.getenv('DB_NAME'))
    # mongo_service.connect()
    # mongo_service.reset_collections() 
    # reset_chroma_db()

    # New chat button functionality
    st.markdown(
        '<a href="/" class="custom-button" role="button" target="_self">╋ New Chat</a>',
        unsafe_allow_html=True
    )

    st.header("Nele.ai - Where Intelligence Meets Security", divider='gray')
    chat_manager = ChatManagement()
    chat_manager.display_sidebar()
    chat_manager.display_conversations()

    # Track whether the file has been processed
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False

    # Track whether the current file has been processed
    if "current_file_processed" not in st.session_state:
        st.session_state.current_file_processed = False

    # Ensure document content name is available before displaying
    if "document_content_name" in st.session_state:
        st.session_state["file_processed"] = True

    # File uploader logic with conditional disabling
    uploaded_file = st.file_uploader("Upload a file (PDF or CSV)", disabled=st.session_state.file_processed, type=["pdf", "csv"])

    # Process the file only if it's uploaded and not already processed
    if uploaded_file and not st.session_state.file_processed:
        uploaded_file_sucess= process_uploaded_file(uploaded_file)

        st.session_state["current_file_processed"] = True

    if "document_content_name" in st.session_state and not st.session_state.current_file_processed:
        if st.session_state.document_content_name:
            st.markdown(f"📄 **{st.session_state['document_content_name']}** {st.session_state['file_size']}") 

    # Initialize conversation chain if not initialized
    if "conversation" not in st.session_state:
        initialize_conversation_chain()
    
    # Display previous messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    handle_user_input()

    if st.session_state.messages:
        if st.button("Delete ✖"):
            chat_id = st.query_params.get("chat_id")
            delete_success = DeleteChatPopup(chat_id)

if __name__ == "__main__":
    main()
