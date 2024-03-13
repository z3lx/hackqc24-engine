from fastapi import FastAPI
from langserve import add_routes
import uvicorn

from chain import ChatBot

if __name__ == "__main__":
    app = FastAPI(
        title="LangChain Server",
        version="1.0",
        description="",
    )

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

    add_routes(
        app,
        bot.get_main(),
        path="/main",
    )

    add_routes(
        app,
        bot.get_add_human_message(),
        path="/add_human_message",
    )

    add_routes(
        app,
        bot.get_add_ai_message(),
        path="/add_ai_message",
    )

    uvicorn.run(app, host="localhost", port=8000)
