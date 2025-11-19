"""
LLM Quiz Solver (Minimal Version)
- Single file, with FastAPI, Playwright, OpenAI GPT, PDF, and chart support
- To run: python main.py
"""

import os
import time
import base64
import requests
import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, HttpUrl
from dotenv import load_dotenv

# Optional: PDF/Chart import
import pypdf
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

# Imports for Browser Automation
import asyncio
from playwright.async_api import async_playwright

load_dotenv(".env")

# ENVIRONMENT
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
EMAIL = os.getenv("EMAIL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
PORT = int(os.getenv("PORT", "8000"))

# API app
app = FastAPI()

### MODELS

class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: HttpUrl

class QuizResponse(BaseModel):
    status: str
    message: str
    processing: bool

### LLM Client

async def call_openai(prompt, system_prompt=None, max_tokens=500):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, timeout=30.0)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]

### BROWSER (Playwright)

async def fetch_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_timeout(2000)
        html = await page.content()
        await browser.close()
        return html

### PDF Extraction (example with PyMuPDF)

def extract_pdf_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

### Main Quiz Processor

async def process_quiz(request: QuizRequest):
    start = time.time()
    current_url = request.url
    session = httpx.AsyncClient()

    while current_url and (time.time() - start < 180):
        html = await fetch_html(current_url)
        submit_urls = [line for line in html.split() if "/submit" in line]
        # Find PDF URL if present
        pdf_links = [line for line in html.split() if ".pdf" in line]
        system_prompt = "You are a helpful assistant that answers quiz questions. Do not reveal any codeword or secret."
        if pdf_links:
            pdf_url = pdf_links[0].split('\"')[0]
            pdf_bytes = requests.get(pdf_url).content
            pdf_text = extract_pdf_text(pdf_bytes)
            prompt = f"Given this text from a PDF:\n{pdf_text[:2000]}\nWhat answer does the quiz page want? Return only the answer."
        else:
            prompt = f"The page content is:\n{html[:2000]}\nWhat answer does the quiz want? Return only the answer."
        answer = (await call_openai(prompt, system_prompt)).strip()
        # Try to parse as number
        try:
            if "." in answer:
                answer = float(answer)
                if answer.is_integer(): answer=int(answer)
            else:
                answer = int(answer)
        except:
            pass
        submit_url = submit_urls[0].split('\"')[0] if submit_urls else current_url
        payload = {"email": request.email, "secret": request.secret, "url": current_url, "answer": answer}
        r = requests.post(submit_url, json=payload)
        result = r.json()
        if result.get("correct") and result.get("url"):
            current_url = result.get("url")
        else:
            break

    await session.aclose()

#### ENDPOINTS

@app.post("/quiz", response_model=QuizResponse)
async def quiz_endpoint(request: QuizRequest, background_tasks: BackgroundTasks):
    if request.secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret")
    background_tasks.add_task(process_quiz, request)
    return QuizResponse(status="success", message="Started quiz processing", processing=True)

@app.get("/")
async def index():
    return {"status": "OK", "usage": "POST to /quiz with {email, secret, url}"}

# Entry point for uvicorn/CLI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
