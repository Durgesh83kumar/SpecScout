# 🔍 SpecScout — AI Laptop Comparison Agent

SpecScout is an AI agent that compares laptops for you. Paste raw specs **or**
just paste a product URL — SpecScout fetches the page, extracts the specs,
and returns a structured comparison table plus an AI-generated verdict
tailored to your specific use case (Gaming, Coding, Student, Video Editing,
Business, or General use).

## Demo

**Input — paste a product URL (or raw specs) for up to 3 laptops:**

![SpecScout input screenshot](screenshots/input.png)

**Output — comparison table + AI verdict:**

![SpecScout comparison output](screenshots/output.png)

Example run: three real Flipkart listings — Dell G15, Acer Aspire 7, and HP
Victus — compared for the **"Student"** use case using nothing but their
product URLs. SpecScout fetched all three pages, extracted clean product
names and specs automatically, and picked the Acer Aspire 7 as best overall
based on its lower weight (portability) and price — reasoning matched to
what actually matters for a student, not just whichever laptop had the
biggest numbers.

## What it does

1. **Add 2–3 laptops** — for each one, either:
   - Paste a product URL (SpecScout fetches the page and extracts specs + name automatically), or
   - Paste raw spec text manually (copy-pasted from any listing)
2. **Select your use case** (Gaming, Coding, Student, Video Editing, Business, General use)
3. **An LLM (Llama 3.3 70B via Groq)** parses the specs and returns:
   - A clean side-by-side comparison table, using the laptops' real product
     names as column headers (Processor, RAM, Storage, Graphics, Display,
     Weight, Price, Battery Life)
   - A verdict: best overall, best value, and best for your specific use case
   - A plain-language summary that stays consistent with the verdict

## Tech stack

- **Python**
- **Streamlit** — UI
- **Groq API (Llama 3.3 70B)** — LLM reasoning and structured JSON output
- **Requests + BeautifulSoup** — fetching and parsing product pages
- **python-dotenv** — API key management

## Setup

1. Get a free Groq API key from [console.groq.com/keys](https://console.groq.com/keys)

2. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/Durgesh83kumar/SpecScout.git
   cd SpecScout
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Add your API key to a `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## How it works (architecture)

```
User provides 2-3 laptops (URL or pasted specs) + selects use case
              │
              ▼
   If URL: fetch page → extract product name (from <title>)
           → extract specs (from <table> elements)
              │
              ▼
   Prompt builder injects specs + real laptop names +
   use-case-specific evaluation criteria (e.g. "for Gaming,
   prioritize GPU/refresh rate"; "for Coding, prioritize RAM/battery")
              │
              ▼
      Groq API (Llama 3.3 70B) generates JSON:
      comparison table (keyed by real laptop names) + verdict + summary
              │
              ▼
   JSON is extracted robustly (regex fallback handles stray
   text around the JSON block) and parsed
              │
              ▼
   Streamlit renders table, verdict (best overall / best value /
   best for use case), and summary
```

This is a genuinely agentic pipeline — SpecScout fetches live external data
and reasons over it, rather than just processing text the user hands it
directly.

## Project status

✅ **Phase 1 — Complete**
- Manual spec paste → AI comparison pipeline working end-to-end
- Structured JSON output rendered as table + verdict

✅ **Phase 2 — Complete**
- Paste a product URL instead of manually copying specs — the app fetches
  and extracts specs (and the product name) automatically
- Use-case-aware evaluation criteria baked into the prompt, so the AI
  reasons about what actually matters for Gaming vs. Coding vs. Student vs.
  Video Editing, instead of just picking the laptop with the biggest number
  on any one spec
- Real laptop names used as table/JSON keys instead of generic
  `laptop_1` / `laptop_2` labels
- Verdict and summary consistency check added to the prompt, so the
  recommendation doesn't contradict itself
- Robust JSON extraction with regex fallback, so a malformed model response
  doesn't crash the app
- Tested end-to-end against multiple real Flipkart listings across several
  use cases (Gaming, Coding, Student, Video Editing)

🔜 **Phase 3 — Planned**
- Browser extension with a "Compare with AI" button on product pages

🔜 **Phase 4 — Planned**
- Generalize beyond laptops to other electronics categories

## Known limitations

- Spec extraction quality depends on how a listing's page is structured;
  some sellers omit fields entirely (e.g. battery life), which SpecScout
  reports honestly as "Not listed by seller" rather than guessing
- Product page scraping is inherently fragile — if a site changes its HTML
  structure, extraction may need adjustment
- This project does not violate any site's ToS by scraping in bulk — a user
  manually supplies one product URL at a time, the same as opening it in a
  browser themselves

## Notes

- `.env` is excluded via `.gitignore`; never commit API keys.