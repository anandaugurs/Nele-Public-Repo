from langchain.callbacks.base import BaseCallbackHandler
import time

# Class for streaming output from LLM (to update the UI with each token generated)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text + "▌")
        time.sleep(0.5)
