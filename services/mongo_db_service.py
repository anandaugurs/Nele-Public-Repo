from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import streamlit as st

class MongoDBConnectionService:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.db = self.client[self.db_name]
            self.client.admin.command('ping')
            # st.toast("You successfully connected to MongoDB!")
        except Exception as e:
            st.error(f"Error connecting to MongoDB: {e}")

    def get_collection(self, collection_name: str):
        if self.db is not None:
            return self.db[collection_name]
        else:
            st.error("No active MongoDB connection. Please connect first.")
            return None
        
    def reset_collections(self):
    
        if self.db is not None:
            collection_names = ['ChatCollection', 'ChatHistoryCollection', 'FileUploadedCollection']
            for collection_name in collection_names:
                collection = self.db[collection_name]

                # Drop the collection
                collection.drop()
                st.info(f"Collection '{collection_name}' has been dropped.")

                self.db.create_collection(collection_name)
                st.success(f"Collection '{collection_name}' has been reset.")
        else:
            st.error("No active MongoDB connection. Please connect first.")

class ChatService:
    def __init__(self, db_connection: MongoDBConnectionService):
        self.db_connection = db_connection

    def create_chat(self, chat_data: dict, chatId: str):
        chat_collection = self.db_connection.get_collection("ChatCollection")
        chat_history_collection = self.db_connection.get_collection("ChatHistoryCollection")

        if chat_collection is not None and chat_history_collection is not None:
            try:
                existing_chat = chat_collection.find_one({"chatId": chatId})

                if existing_chat:
                    inserted_history_id = chat_history_collection.insert_one(chat_data).inserted_id
                    return
                chat_collection_data = {
                    "chatId": chat_data.get('chatId'), 
                    "userId": chat_data.get('userId'), 
                    "userPrompt":chat_data.get('userPrompt'),
                    "createdAt": datetime.now(),
                }
                self.store_uploaded_file({"chatId": chatId, "uploaded_document":st.session_state.get("metadatas", "")})
                inserted_id = chat_collection.insert_one(chat_collection_data).inserted_id
                inserted_history_id = chat_history_collection.insert_one(chat_data).inserted_id
            except Exception as e:
                st.error(f"Error inserting chat document: {e}")
        else:
            st.warning("No active MongoDB collection. Please provide a valid collection.")

    def delete_chat(self, chatId: str):
        """
        Deletes the chat and its history by chatId from both ChatCollection and ChatHistoryCollection.
        """
        chat_collection = self.db_connection.get_collection("ChatCollection")
        chat_history_collection = self.db_connection.get_collection("ChatHistoryCollection")

        if chat_collection is not None and chat_history_collection is not None:
            try:
                # Delete the chat from ChatCollection
                chat_collection.delete_one({"chatId": chatId})

                # Delete corresponding history from ChatHistoryCollection
                chat_history_collection.delete_many({"chatId": chatId})

                return f"Chat with chatId {chatId} and its history have been deleted."
            
            except Exception as e:
                st.error(f"Error deleting chat or history: {e}")
        else:
            st.warning("No active MongoDB collection. Please provide a valid collection.")

    def chat_history(self, user_id: str):
        chat_collection = self.db_connection.get_collection("ChatCollection")
        if chat_collection is not None:
            try:
                chat_history = chat_collection.find({"userId": user_id}).sort("createdAt", -1)
                return list(chat_history)
            except Exception as e:
                st.error(f"Error retrieving chat history: {e}")
                return []
        else:
            st.warning("No active MongoDB collection. Please provide a valid collection.")
            return []

    def get_chat_details(self, chat_id: str):
        """
        Retrieves chat details and uploaded files for a specific chat ID.
        """
        try:
            # Get collections
            chat_history_collection = self.db_connection.get_collection("ChatHistoryCollection")
            file_uploaded_collection = self.db_connection.get_collection("FileUploadedCollection")

            # Check if the collections are valid
            if chat_history_collection is None or file_uploaded_collection is None:
                st.warning("No active MongoDB collections. Please provide valid collections.")
                return {"chat_details": [], "uploaded_files": []}

            # Retrieve chat history
            chat_details = list(chat_history_collection.find({"chatId": chat_id}))

            # Retrieve uploaded files
            uploaded_files = list(file_uploaded_collection.find({"chatId": chat_id}))

            # Return both chat details and uploaded files
            return {"chat_details": chat_details, "uploaded_files": uploaded_files}

        except Exception as e:
            st.error(f"Error retrieving chat details or uploaded files: {e}")
            return {"chat_details": [], "uploaded_files": []}


    def store_uploaded_file(self, document_data: dict):
       
        file_uploaded_collection = self.db_connection.get_collection("FileUploadedCollection")

        if file_uploaded_collection is not None:
            try:
                uploaded_document = document_data.get("uploaded_document")
                if uploaded_document:
                    # Check if a document with the same content and user already exists
                    existing_document = file_uploaded_collection.find_one({
                        "uploaded_document": document_data.get("uploaded_document"),
                        "chatId": document_data.get("chatId")
                    })

                    if not existing_document:
                        # Access the file name from the uploaded_document
                        if not uploaded_document or not isinstance(uploaded_document, dict):
                            print("Invalid uploaded_document structure in document data.")
                        
                        file_name = uploaded_document.get("file_name")
                        if not file_name:
                            print("File name is missing in the uploaded document.")
                            
                        # Check if the filename already exists with different content
                        existing_filename_document = file_uploaded_collection.find_one({
                            "file_name": file_name
                        })

                        if existing_filename_document and existing_filename_document.get("uploaded_document") != uploaded_document:
                            # Generate a unique filename
                            import uuid
                            file_name_parts = file_name.rsplit('.', 1)
                            if len(file_name_parts) == 2:
                                unique_file_name = f"{file_name_parts[0]}_{uuid.uuid4().hex[:8]}.{file_name_parts[1]}"
                            else:
                                unique_file_name = f"{file_name}_{uuid.uuid4().hex[:8]}"
                            uploaded_document["file_name"] = unique_file_name

                        # Update the document data with the modified uploaded_document
                        document_data["uploaded_document"] = uploaded_document

                        # Insert the document
                        inserted_document_id = file_uploaded_collection.insert_one(document_data).inserted_id
                else:
                    print("No Document")
            except Exception as e:
                st.error(f"Error inserting the document: {e}")
                print(e, "=-----------------")
        else:
            st.warning("No active MongoDB collection. Please provide a valid collection.")






class UserService:
    def __init__(self, collection):
        self.collection = collection

    def create_user(self, user_data: dict):
        if self.collection is not None:
            try:
                inserted_id = self.collection.insert_one(user_data).inserted_id
                st.info(f"User created with ID: {inserted_id}")
            except Exception as e:
                st.error(f"Error inserting user document: {e}")
        else:
            st.error("No active MongoDB collection. Please provide a valid collection.")















# # MongoDB Connection
# connection = MongoDBConnectionService(uri="your_mongodb_uri", db_name="your_db_name")
# connection.connect()

# # Collections
# # user_collection = connection.get_collection("users")
# chat_collection = connection.get_collection("chats")

# # Services
# # user_service = UserService(user_collection)
# chat_service = ChatService(chat_collection)

# # Example Usage
# # user_service.create_user({"name": "Alice", "email": "alice@example.com"})
# chat_service.create_chat({"userId": "123", "message": "Hello, world!"})
# chat_history = chat_service.chat_history("123")
# print(chat_history)
