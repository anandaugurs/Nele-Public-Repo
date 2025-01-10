from services.mongo_db_service import MongoDBConnectionService
from services.mongo_db_service import ChatService
import streamlit as st
import os
import time

class ChatManagement:

    def __init__(self, title="Chat Management"):
        self.title = title
        self.user_id = os.getenv('USER_ID')

    def connect_to_db(self):
        """Connect to the MongoDB database."""
        connection = MongoDBConnectionService(uri=os.getenv('MONGODB_URL'), db_name=os.getenv('DB_NAME'))
        connection.connect()
        return connection

    def display_sidebar(self):
        col1, col2 = st.sidebar.columns([2, 3])
       
        st.sidebar.header("Chat History", divider='gray')

        connection = self.connect_to_db()

        chat_service = ChatService(db_connection=connection)
     
        chat_history = chat_service.chat_history(self.user_id)

        active_chat_id = st.query_params.get("chat_id", [None])

        for content in chat_history:
            
            chatId = content['chatId']
            promptTitle = content['userPrompt']
            truncated_title = (promptTitle[:25] + ' ...') if len(promptTitle) > 25 else promptTitle

            active_class = "active" if active_chat_id == chatId else ""
            
            st.sidebar.markdown(
                f'<div class="cstm-div {active_class}"><a href="/?chat_id={chatId}" class="sidebar_text" target="_self">{truncated_title.capitalize()}</a></div>',
                unsafe_allow_html=True
            )

  
    def display_conversations(self):
        """Displays the conversation details and uploaded documents for a specific chat."""
        chat_id = st.query_params.get('chat_id')

        try:
            # Display the loading spinner while fetching data
            with st.spinner('Loading chat details...'):
                # Establish database connection
                connection = self.connect_to_db()
                chat_service = ChatService(db_connection=connection)

                # Load chat details only if a new chat ID is provided
                if st.session_state.get("loaded_chat_id") != chat_id:
                    # Fetch chat details and uploaded files
                    details = chat_service.get_chat_details(chat_id)

                    # Reset session state for the new chat
                    st.session_state.messages = []
                    st.session_state.loaded_chat_id = chat_id
                    st.session_state.file_processed = False  # Reset file state on new chat

                    chat_details = details.get("chat_details", [])
                    uploaded_files = details.get("uploaded_files", [])

                    # Display chat messages
                    if chat_details:
                        for chat in chat_details:
                            prompt = chat.get('userPrompt', '')
                            response = chat.get('response', '')

                            st.session_state.messages.append({"role": "user", "content": prompt})
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.warning("No chat details found for the provided chat ID.")

                    # Handle uploaded documents
                    if uploaded_files and not st.session_state.get("file_processed", False):
                        for uploaded_file in uploaded_files:
                            document = uploaded_file.get('uploaded_document', {})
                            file_name = document.get('file_name', 'Unknown File')
                            content = document.get('content', 'No content available')
                            file_size = document.get('file_size', '0KB')

                            # Store the document content in session state
                            st.session_state["document_content"] = content
                            st.session_state["document_content_name"] = file_name
                            st.session_state["file_size"] = file_size 
                            
        except Exception as e:
            st.error(f"An error occurred while retrieving chat details: {e}")

    def delete_all_chats(self, chatId):
        try:
            # Establish connection to the database
            connection = self.connect_to_db()
            
            # Initialize the chat service with the DB connection
            chat_service = ChatService(db_connection=connection)
            
            # Call the delete_chat method to delete the chat
            delete_status = chat_service.delete_chat(chatId)
            return delete_status
        except Exception as e:
            # Handle any errors that occur during the deletion process
            print(f"Error deleting chat with ID {chatId}: {e}")