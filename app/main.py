from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Welcome to Examinie AI API!"}