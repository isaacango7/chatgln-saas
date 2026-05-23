from fastapi import FastAPI

from routes.ai import router

app = FastAPI()

app.include_router(router)

@app.get("/")

def home():

    return {

        "message":
            "ChatGLN Backend Online 🚀"

    }
