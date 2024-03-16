import os

from chatbot import ChatBot

os.environ["LANGCHAIN_TRACING_V2"] = "true"

bot = ChatBot(
    model_name="gpt-3.5-turbo",
    embeddings_model_name="text-embedding-3-small",
    db_type="Chroma",
    db_path="./db",
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 50,
        "lambda_mult": 0.25
    }
)

while True:
    message = input("You: ")
    response = bot.get_response(message)
    print(f"Bot: {response}")
