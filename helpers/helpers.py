import streamlit as st
import uuid

def set_chat_id():
    chat_id = st.query_params.get("chat_id")

    if chat_id is None:
        
        chat_id = str(uuid.uuid4())

        st.query_params["chat_id"] = chat_id

    return chat_id

