# NP Digital — Blog Outline Generator

Generates SEO/GEO-optimized blog outlines using Claude and pushes them directly to Google Docs.

## Setup

### 1. Clone and deploy to Streamlit Community Cloud
- Fork or push this repo to GitHub
- Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo → `app.py`

### 2. Add secrets in Streamlit
In your app dashboard → Settings → Secrets, add:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
APPS_SCRIPT_URL = "https://script.google.com/macros/s/.../exec"
```

### 3. Apps Script (Google Docs output)
Deploy the Apps Script from the setup guide in the app sidebar.

## Cost
~$0.003–0.006 per outline using Claude Haiku.
