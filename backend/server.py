# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Allow importing core.py from the parent folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core import get_comparison, fetch_specs_from_url

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="SpecScout API")

# Lets the browser extension (running on flipkart.com) call this local server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompareRequest(BaseModel):
    laptops: list[str]
    names: list[str]
    use_case: str


class CompareUrlsRequest(BaseModel):
    urls: list[str]
    use_case: str


@app.get("/")
def health_check():
    return {"status": "SpecScout API is running"}


@app.post("/compare")
def compare(req: CompareRequest):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set on server"}

    filled = [l for l in req.laptops if l.strip()]
    if len(filled) < 2:
        return {"error": "Need at least 2 laptops with specs"}

    result = get_comparison(api_key, req.laptops, req.names, req.use_case)
    return result


@app.post("/compare-urls")
def compare_urls(req: CompareUrlsRequest):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set on server"}

    names, specs = [], []
    for url in req.urls:
        name, spec_text = fetch_specs_from_url(url)
        names.append(name)
        specs.append(spec_text)

    filled = [s for s in specs if s.strip()]
    if len(filled) < 2:
        return {"error": "Could not extract usable specs from at least 2 of the given URLs"}

    result = get_comparison(api_key, specs, names, req.use_case)
    return result