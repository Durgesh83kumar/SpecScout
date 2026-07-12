import streamlit as st
import os
from dotenv import load_dotenv
from core import get_comparison, fetch_specs_from_url


load_dotenv()
st.set_page_config(page_title="SpecScout", page_icon="💻", layout="wide")
st.title("💻 SpecScout — Laptop Comparison Agent")

api_key_input = os.getenv("GROQ_API_KEY")

with st.sidebar:
    if api_key_input:
        st.success("API key loaded ✅")
    else:
        st.error("No API key found. Add GROQ_API_KEY to your .env file.")




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