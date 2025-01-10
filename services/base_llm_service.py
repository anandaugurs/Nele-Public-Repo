class BaseLLMService:
    def __init__(self, temperature=0.7):
        self.temperature = temperature

    def initialize_llm(self):
        raise NotImplementedError("This method should be implemented in subclasses.")
