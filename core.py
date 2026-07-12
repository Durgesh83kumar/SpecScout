# core.py
from groq import Groq
import json
import re
import requests
from bs4 import BeautifulSoup

USE_CASE_CRITERIA = {
    "Video editing": "Prioritize CPU multi-core performance, RAM (32GB+ preferred over 16GB), GPU VRAM for render acceleration, and color-accurate displays. Refresh rate above 60Hz is NOT a meaningful factor for video editing.",
    "Gaming": "Prioritize GPU model/VRAM, high refresh rate (144Hz+), and CPU single-core speed.",
    "Coding": "Prioritize RAM (16GB+), fast SSD, and battery life. GPU and refresh rate are low priority.",
    "Student": "Prioritize battery life, weight/portability, and price. High-end GPU is unnecessary.",
    "Business": "Prioritize battery life, portability, keyboard quality, and security features. GPU is unnecessary.",
    "General use": "Prioritize balanced performance and price. No single spec should dominate the decision."
}


def fetch_specs_from_url(url):
    """Fetch a product page server-side and extract a clean name + spec text.
    Used by both the Streamlit app and the browser extension's backend."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        title_tag = soup.find("title")
        raw_title = title_tag.get_text(strip=True) if title_tag else ""
        if " - (" in raw_title:
            name = raw_title.split(" - (")[0].strip()
        elif "Price in India" in raw_title:
            name = raw_title.split("Price in India")[0].strip()
        else:
            name = raw_title.split("|")[0].strip()
        name = (name or "Unknown Laptop")[:60]

        tables = soup.find_all("table")
        specs = "\n".join(t.get_text(separator="\n", strip=True) for t in tables) if tables \
                else soup.get_text(separator="\n", strip=True)[:3000]

        return name, specs
    except Exception:
        return "Unknown Laptop", ""


def build_prompt(laptops, names, use_case):
    laptops_text = "\n\n".join(
        f"{names[i]}:\n{spec}" for i, spec in enumerate(laptops) if spec.strip()
    )
    active_names = [names[i] for i, spec in enumerate(laptops) if spec.strip()]
    criteria = USE_CASE_CRITERIA.get(use_case, "")
    example_row = ", ".join(f'"{n}": "..."' for n in active_names)

    return f"""You are a laptop buying expert. Compare these laptops for: {use_case}.

Evaluation criteria for this use case: {criteria}

{laptops_text}

IMPORTANT — Field extraction rules:
- For the "Graphics" row, always combine the GPU model AND its VRAM/memory capacity into one value. Merge fields like "Graphic Processor" and "Dedicated Graphic Memory Capacity" if given separately.
- For "Battery Life", only write a value if explicitly mentioned. Otherwise write "Not listed by seller".

IMPORTANT — Verdict definitions:
- "best_overall" = the single laptop offering the strongest balance of performance AND price together for this use case. Do not pick a laptop as best_overall based on specs alone if a similarly-capable laptop is meaningfully cheaper — factor price into best_overall itself, not just into best_value.
- "best_value" = the laptop with the best performance-per-rupee, which may be the same as best_overall or different if a cheaper laptop sacrifices only minor performance.
- The summary must justify best_overall using the SAME reasoning (including price) that led to picking it — never argue for a different laptop than best_overall in the summary.

Return ONLY valid JSON, no markdown, in this structure. Use these EXACT laptop names as keys: {active_names}

{{
  "comparison_table": [
    {{"spec": "Processor", {example_row}}},
    {{"spec": "RAM", {example_row}}},
    {{"spec": "Storage", {example_row}}},
    {{"spec": "Graphics", {example_row}}},
    {{"spec": "Display", {example_row}}},
    {{"spec": "Price", {example_row}}}
  ],
  "verdict": {{
    "best_overall": "the exact name of one laptop from the list above",
    "best_value": "the exact name of one laptop from the list above",
    "best_for_use_case": "the exact name of one laptop from the list above — never write the use case itself here, always a laptop name"
  }},
  "summary": "2-3 sentences that must directly justify and agree with best_overall."
}}

Before answering, double check that your summary names the SAME laptop as best_overall."""


def extract_json(text):
    text = text.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group()) if match else json.loads(text)


def get_comparison(api_key, laptops, names, use_case):
    client = Groq(api_key=api_key)
    prompt = build_prompt(laptops, names, use_case)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return extract_json(response.choices[0].message.content)