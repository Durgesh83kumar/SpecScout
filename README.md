# 🔍 SpecScout — AI Laptop Comparison Agent

SpecScout is an AI agent that compares laptops for you — from a web app, or
directly from your browser while shopping. Add laptops by URL (or paste raw
specs), pick your use case, and get a structured comparison table plus an
AI-generated verdict tailored to what actually matters for that use case.

**🚀 Live demo:** [specscout-tpy7mmkehn9cpudbjui5th.streamlit.app](https://specscout-tpy7mmkehn9cpudbjui5th.streamlit.app/)

> **⚠️ Important — what works where:**
> - **"Paste specs" mode (Phase 1)** works everywhere — on the live Streamlit
>   demo above, and when run locally.
> - **"Paste URL" mode (Phase 2)** and the **Chrome extension (Phase 3)**
>   only work when the app/backend is **run locally**. Flipkart actively
>   blocks scraping requests coming from cloud-hosted IPs (like Streamlit
>   Community Cloud's servers), so URL-based fetching fails on the deployed
>   app even though it works fine locally, where the request comes from
>   your own machine's IP.
>
> To try URL-paste or the Chrome extension, follow the **"Run it locally"**
> steps below.

---

## Demo

*Screenshots below are from the live deployed app, using "Paste specs" mode.*

**Streamlit app — paste specs or URLs, compare up to 3 laptops:**

![SpecScout input screenshot](screenshots/input.png)

**Comparison output — table + AI verdict:**

![SpecScout comparison output](screenshots/output.png)

**Browser extension — add laptops straight from Flipkart tabs, compare in the popup:**

![SpecScout browser extension demo](screenshots/extension.png)

Example: three real laptops — an i7 13th Gen / RTX 3050 machine, an Intel
Core 7 240H laptop, and a 14-inch 2.8K OLED Intel Core 7 machine — compared
for **Video editing**. SpecScout weighed processor generation, RAM, display
quality (2.8K OLED with 100% DCI-P3), and price together, and picked the
OLED laptop as **Best Overall**, **Best Value**, and **Best for Video
editing** — with reasoning that explains *why*, not just a table with a
laptop name circled.

**Live app — input screen ("Paste specs" mode, 3 laptops, use-case selector):**

![SpecScout live demo input screen](screenshots/streamlit-demo-input.png)

**Live app — comparison table + AI verdict on the deployed Streamlit app:**

![SpecScout live demo verdict output](screenshots/streamlit-demo-verdict.png)

## What it does

**Two ways to use SpecScout, same AI engine underneath:**

1. **Web app (Streamlit)** — add 2–3 laptops by pasting a product URL or raw
   spec text, select a use case, get a full comparison table + verdict
   - Pasting raw specs works both on the **live deployed app** and locally
   - Pasting a URL only works **locally** (see note above — Flipkart blocks
     scraping from cloud IPs)
2. **Browser extension (Chrome)** — while browsing Flipkart, click "Add this
   laptop from current tab" on each product page you're considering, then
   compare them from the extension popup without leaving your browsing flow
   - Requires the **local** FastAPI backend to be running; not usable
     against the deployed app

Both paths use the same reasoning: an LLM (Llama 3.3 70B via Groq) evaluates
laptops against criteria specific to the selected use case — e.g. for Gaming
it weighs GPU/refresh rate, for Coding it weighs RAM/battery life, for
Student it weighs weight/portability/price, for Video Editing it weighs
display color accuracy/RAM/storage — rather than just picking whichever
laptop has the biggest number on any single spec.

## Tech stack

- **Python** — core logic and both server implementations
- **Streamlit** — web app UI (deployed on Streamlit Community Cloud)
- **FastAPI + Uvicorn** — backend API for the browser extension
- **Groq API (Llama 3.3 70B)** — LLM reasoning and structured JSON output
- **Requests + BeautifulSoup** — server-side page fetching and spec extraction
- **Chrome Extension (Manifest V3)** — browser-based UI, calls the backend directly
- **python-dotenv** — API key management

## Project structure

```
SpecScout/
├── app.py                  # Streamlit web app
├── core.py                 # Shared logic: prompt building, LLM calls,
│                            # URL fetching — used by both app.py and the backend
├── backend/
│   └── server.py            # FastAPI backend the extension talks to
└── extension/
    ├── manifest.json         # Chrome extension config
    ├── popup.html              # Extension popup UI
    └── popup.js                 # Extension popup logic
                                  # (no content script needed — the popup
                                  #  reads the active tab's URL directly)
```

## Setup

### Try it instantly — no setup required
The Streamlit web app is live and ready to use for **"Paste specs" mode**:
👉 **[specscout-tpy7mmkehn9cpudbjui5th.streamlit.app](https://specscout-tpy7mmkehn9cpudbjui5th.streamlit.app/)**

For **URL-paste mode** or the **Chrome extension**, run it locally instead
(steps below) — the deployed app can't fetch Flipkart URLs directly, since
Flipkart blocks scraping requests from cloud IPs.

### Run it locally (required for URL-paste and the Chrome extension)

#### 1. Get a free Groq API key
[console.groq.com/keys](https://console.groq.com/keys)

#### 2. Clone and install
```bash
git clone https://github.com/Durgesh83kumar/SpecScout.git
cd SpecScout
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Add your API key
```
# .env
GROQ_API_KEY=your_key_here
```

#### 4. Run the web app
```bash
streamlit run app.py
```

#### 5. Run the backend (needed for the browser extension)
```bash
uvicorn backend.server:app --reload --port 8000
```

#### 6. Load the browser extension
1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked** → select the `extension/` folder
4. Visit a Flipkart laptop page → click the SpecScout icon → **Add this
   laptop from current tab**
5. Repeat on a second (and optional third) laptop page
6. Pick a use case → **Compare**

The backend (step 5) must be running locally for the extension to work —
the extension is a local-first companion to the deployed web app.

## How it works (architecture)

```
                    ┌─────────────────┐
                    │     core.py      │
                    │ fetch_specs_from_url()
                    │ build_prompt()    │
                    │ get_comparison()   │
                    └───────┬─────────┘
                            │
              ┌─────────────┴─────────────┐
              │                             │
      ┌───────▼───────┐           ┌────────▼────────┐
      │   app.py        │           │ backend/server.py │
      │  (Streamlit)     │           │    (FastAPI)        │
      └───────┬───────┘           └────────┬────────┘
              │                             │
      User pastes specs/URL         Browser extension sends
      directly in the browser       the current tab's URL
```

**Extension flow specifically:**
```
User clicks "Add this laptop from current tab" on a Flipkart tab
        │
        ▼
Popup reads the active tab's URL directly via chrome.tabs.query
(no content script, no in-browser DOM scraping)
        │
        ▼
On "Compare": extension POSTs collected URLs + use case to
http://127.0.0.1:8000/compare-urls
        │
        ▼
Backend fetches each URL server-side (requests + BeautifulSoup),
extracts product name + specs
        │
        ▼
Backend builds a use-case-aware prompt and calls Groq (Llama 3.3 70B)
        │
        ▼
Structured JSON (table + verdict + summary) returned to the popup
```

This is a genuinely agentic pipeline: the extension and backend fetch live
external data and reason over it autonomously, rather than only processing
text a user hands over directly.

## Project status

✅ **Phase 1 — Complete**
Manual spec paste → AI comparison, structured table + verdict.

✅ **Phase 2 — Complete**
Paste a product URL instead of specs — the Streamlit app fetches and
extracts specs and product names automatically. Use-case-aware evaluation
criteria added, verdict/summary consistency enforced, robust JSON parsing.

✅ **Phase 3 — Complete**
- Chrome extension (Manifest V3) lets you add laptops directly from
  Flipkart product pages and compare them without leaving the browser
- Shared `core.py` module used by both the Streamlit app and a new FastAPI
  backend, avoiding duplicated logic
- Extension sends tab URLs to the backend, which does the actual page
  fetching server-side — more reliable than in-browser DOM scraping, since
  it reuses the exact fetch/parse logic already proven in Phase 2
- Verdict logic tightened further: "best overall" now explicitly factors in
  price rather than pure specs, and each verdict field is constrained to
  always contain a laptop name (fixing an earlier bug where a field
  occasionally echoed the use case label instead)
- Backend hardened: every route now returns structured JSON — including
  on unexpected errors or upstream rate limits — instead of ever crashing
  with a raw 500, so the extension can always parse the response and show
  a clean message
- Tested end-to-end across multiple real Flipkart listings and use cases

✅ **Deployment — Complete**
Streamlit web app deployed and publicly accessible at
[specscout-tpy7mmkehn9cpudbjui5th.streamlit.app](https://specscout-tpy7mmkehn9cpudbjui5th.streamlit.app/)

🔮 **Phase 4 — Future work**
Generalize beyond laptops to other electronics categories (phones,
earbuds, monitors, etc.), and extend the extension/backend to other retail
sites beyond Flipkart.

## Known limitations

- Spec extraction quality depends on how a listing's page is structured;
  fields a seller omits (e.g. battery life) are reported honestly as "Not
  listed by seller" rather than guessed
- **URL-paste mode and the Chrome extension only work locally.** Flipkart
  blocks scraping requests from cloud-hosted IPs (like Streamlit Community
  Cloud), so `fetch_specs_from_url` fails on the deployed app even though
  it works reliably when run from a local machine. "Paste specs" mode has
  no such restriction and works identically everywhere.
- The FastAPI backend for the browser extension must be running locally —
  only the Streamlit web app's "Paste specs" mode is currently usable via
  the public deployment
- Currently scoped to Flipkart; other retailers would need their own page
  parsing adjustments in `fetch_specs_from_url`
- LLM calls run on Groq's free tier, which has a daily token cap; heavy
  back-to-back testing can occasionally hit that limit — this surfaces as
  a clean rate-limit error message rather than a crash

## Notes

- `.env` is excluded via `.gitignore`; never commit API keys
- The extension fetches pages server-side via the backend rather than
  scraping the live rendered DOM in-browser — this sidesteps issues with
  sites that lazy-load or tab-switch content client-side