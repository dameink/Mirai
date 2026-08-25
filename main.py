from fastapi import FastAPI
from core.response import generate_response

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Mirai is alive!"
    }


@app.post("/chat")
def chat(message: str):
    response = generate_response(message)

    return {
        "mirai": response
    }