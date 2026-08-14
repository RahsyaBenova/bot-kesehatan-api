import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Ambil API key dari Environment Variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
Anda adalah asisten konsultan informasi kesehatan.
1. Berikan edukasi dan saran kesehatan umum yang aman.
2. Ingatkan pengguna bahwa ini bukan diagnosis dokter resmi.
3. Arahkan ke faskes/IGD jika ada tanda bahaya.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

class ChatRequest(BaseModel):
    message: str

@app.get("/api")
def root():
    return {"status": "Bot Kesehatan Aktif"}

@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        res = model.generate_content(req.message)
        return {"response": res.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
