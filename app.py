import os
import dotenv
from fastapi import FastAPI
from simple_rag import RAGSystem
import uvicorn
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

dotenv.load_dotenv()

DB_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
rag_system = RAGSystem(DB_URI)

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(response: Question):
    answer = rag_system.run(response.question)
    return {"answer": answer}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)