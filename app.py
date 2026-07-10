import streamlit as st
from groq import Groq
import re
import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="SpecScout", page_icon="💻", layout="wide")
st.title("💻 SpecScout — Laptop Comparison Agent")

api_key_input = os.getenv("GROQ_API_KEY")

with st.sidebar:
    if api_key_input:
        st.success("API key loaded ✅")
    else:
        st.error("No API key found. Add GROQ_API_KEY to your .env file.")


def fetch_specs_from_url(url):
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

        name = name if name else "Unknown Laptop"
        name = name[:60]  # safety cap in case a title has no clean break point

        tables = soup.find_all("table")
        specs = "\n".join(t.get_text(separator="\n", strip=True) for t in tables) if tables \
                else soup.get_text(separator="\n", strip=True)[:3000]

        return name, specs
    except Exception as e:
        st.warning(f"Couldn't fetch specs from that URL ({e}). Try pasting specs manually instead.")
        return "Unknown Laptop", ""


def laptop_input(label):
    mode = st.radio(f"{label} input", ["Paste specs", "Paste URL"], horizontal=True, key=f"{label}_mode")
    if mode == "Paste specs":
        specs = st.text_area(f"{label} specs", height=180, key=f"{label}_text")
        return label, specs
    else:
        url = st.text_input(f"{label} product URL", key=f"{label}_url")
        if url:
            return fetch_specs_from_url(url)
        return label, ""


col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Laptop 1")
    name1, laptop1 = laptop_input("Laptop 1")
with col2:
    st.subheader("Laptop 2")
    name2, laptop2 = laptop_input("Laptop 2")
with col3:
    st.subheader("Laptop 3 (optional)")
    name3, laptop3 = laptop_input("Laptop 3")

use_case = st.selectbox(
    "What do you need the laptop for?",
    ["General use", "Coding", "Gaming", "Video editing", "Student", "Business"]
)


USE_CASE_CRITERIA = {
    "Video editing": "Prioritize CPU multi-core performance, RAM (32GB+ preferred over 16GB), GPU VRAM for render acceleration, and color-accurate displays. Refresh rate above 60Hz is NOT a meaningful factor for video editing.",
    "Gaming": "Prioritize GPU model/VRAM, high refresh rate (144Hz+), and CPU single-core speed.",
    "Coding": "Prioritize RAM (16GB+), fast SSD, and battery life. GPU and refresh rate are low priority.",
    "Student": "Prioritize battery life, weight/portability, and price. High-end GPU is unnecessary.",
    "Business": "Prioritize battery life, portability, keyboard quality, and security features. GPU is unnecessary.",
    "General use": "Prioritize balanced performance and price. No single spec should dominate the decision."
}


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
- For the "Graphics" row, always combine the GPU model AND its VRAM/memory capacity into one value, e.g. "NVIDIA GeForce RTX 3050 (4 GB)". These often appear as two separate raw fields like "Graphic Processor" and "Dedicated Graphic Memory Capacity" — merge them. If VRAM truly isn't present anywhere in the specs, write just the GPU name with no memory value, but check carefully before omitting it.
- For "Battery Life", only write a value if the raw specs explicitly mention battery hours or Wh capacity. Otherwise write "Not listed by seller" instead of "Not specified".

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
    "best_overall": "...",
    "best_value": "...",
    "best_for_use_case": "..."
  }},
  "summary": "2-3 sentences that must directly justify and agree with best_overall — do not recommend a different laptop than best_overall names. Base your reasoning on the evaluation criteria given above, not on which spec has the biggest number."
}}

Use the exact laptop names given above as JSON keys in comparison_table, not generic labels like laptop_1.
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
    )
    return extract_json(response.choices[0].message.content)


if st.button("🔍 Compare Laptops"):
    laptops = [laptop1, laptop2, laptop3]
    names = [name1, name2, name3]
    filled = [l for l in laptops if l.strip()]

    if len(filled) < 2:
        st.error("Add at least 2 laptops (paste specs or a URL).")
    else:
        with st.spinner("Comparing..."):
            result = get_comparison(api_key_input, laptops, names, use_case)

            st.subheader("📊 Comparison Table")
            st.table(result["comparison_table"])

            st.subheader("🏆 Verdict")
            st.success(f"**Best Overall:** {result['verdict']['best_overall']}")
            st.info(f"**Best Value:** {result['verdict']['best_value']}")
            st.info(f"**Best for {use_case}:** {result['verdict']['best_for_use_case']}")
            st.write(result["summary"])