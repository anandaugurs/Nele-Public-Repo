from .base_llm_service import BaseLLMService
import os

class OllamaService(BaseLLMService):
    def __init__(self, temperature=0.7):
        super().__init__(temperature)
        self.base_url = os.getenv('PRODUCTION_LLM_ENDPOINT')
        self.model = os.getenv('MODEL_PATH')

    def initialize_llm(self):
        from langchain.llms import Ollama
        return Ollama(base_url=self.base_url, model=self.model)
