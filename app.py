import streamlit as st
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Laptop Compare AI", page_icon="💻", layout="wide")
st.title("💻 Laptop Comparison Agent")


api_key_input = os.getenv("GROQ_API_KEY")

with st.sidebar:
    if api_key_input:
        st.success("API key loaded ✅")
    else:
        st.error("No API key found. Add GEMINI_API_KEY to your .env file.")

col1, col2, col3 = st.columns(3)
with col1:
    laptop1 = st.text_area("Laptop 1", height=180)
with col2:
    laptop2 = st.text_area("Laptop 2", height=180)
with col3:
    laptop3 = st.text_area("Laptop 3 (optional)", height=180)

use_case = st.selectbox(
    "What do you need the laptop for?",
    ["General use", "Coding", "Gaming", "Video editing", "Student", "Business"]
)

def build_prompt(laptops, use_case):
    laptops_text = "\n\n".join(
        f"Laptop {i+1}:\n{spec}" for i, spec in enumerate(laptops) if spec.strip()
    )
    return f"""You are a laptop buying expert. Compare these laptops for: {use_case}.

{laptops_text}

Return ONLY valid JSON, no markdown, in this structure:
{{
  "comparison_table": [
    {{"spec": "Processor", "laptop_1": "...", "laptop_2": "..."}},
    {{"spec": "RAM", "laptop_1": "...", "laptop_2": "..."}}
  ],
  "verdict": {{
    "best_overall": "...",
    "best_value": "...",
    "best_for_use_case": "..."
  }},
  "summary": "2-3 sentence recommendation"
}}"""

def get_comparison(api_key, laptops, use_case):
    client = Groq(api_key=api_key)
    prompt = build_prompt(laptops, use_case)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

if st.button("🔍 Compare Laptops"):
    laptops = [laptop1, laptop2, laptop3]
    filled = [l for l in laptops if l.strip()]

    if len(filled) < 2:
        st.error("Paste at least 2 laptops.")
    else:
        with st.spinner("Comparing..."):
            result = get_comparison(api_key_input, laptops, use_case)

            st.subheader("📊 Comparison Table")
            st.table(result["comparison_table"])

            st.subheader("🏆 Verdict")
            st.success(result["verdict"]["best_overall"])
            st.success(result["summary"])