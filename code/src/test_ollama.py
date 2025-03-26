#from langchain.llms import Ollama
from langchain_ollama import OllamaLLM

# Choose a small model
model_name = "gemma:latest"  # Change to 'mistral', 'gemma', or 'phi' if needed

# Initialize Ollama LLM
llm = OllamaLLM(model=model_name)

# Run a quick test
response = llm.invoke("how to speed up inference in gemma")
print("Ollama Response:", response)

