import streamlit as st
import anthropic
import json
import requests

st.set_page_config(page_title="NP Digital — Blog Outline Generator", page_icon="📝", layout="wide")

# ── Styles ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #F5F3EE; }
  [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DDD9D0; }
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size: 13px; }
  .block-container { padding-top: 2rem; }
  h1 { font-size: 22px !important; font-weight: 600 !important; color: #1A1916 !important; }
  h2 { font-size: 16px !important; font-weight: 600 !important; color: #1A1916 !important; }
  h3 { font-size: 14px !important; font-weight: 500 !important; color: #6B6760 !important; }
  .stButton > button {
    background: #D4541A; color: white; border: none;
    font-weight: 600; border-radius: 8px; padding: 10px 24px;
    font-size: 14px; width: 100%;
  }
  .stButton > button:hover { background: #A83F12; color: white; }
  .stSelectbox label, .stTextInput label, .stTextArea label {
    font-size: 12px !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.06em; color: #6B6760 !important;
  }
  .outline-box {
    background: white; border: 1px solid #DDD9D0; border-radius: 10px;
    padding: 24px; margin-top: 16px;
  }
  .tag { display:inline-block; background:#EBF5F0; color:#2D6A4F;
         font-size:11px; font-weight:600; padding:3px 10px;
         border-radius:20px; margin-bottom:16px; }
</style>
""", unsafe_allow_html=True)

# ── Default clients ──────────────────────────────────────────────────────────
DEFAULT_CLIENTS = {
    "Mitsubishi Motors Canada": {
        "industry": "Automotive — Canada",
        "brief": """TARGET LOCATION: Canada only.

VEHICLES (4 nameplates only — Mirage is discontinued, never mention it):
1. Outlander PHEV (top seller, plug-in hybrid SUV) — https://www.mitsubishi-motors.ca/en/vehicles/outlander-phev
2. Outlander (gas SUV) — https://www.mitsubishi-motors.ca/en/vehicles/outlander
3. Eclipse Cross (compact SUV) — https://www.mitsubishi-motors.ca/en/vehicles/eclipse-cross
4. RVR (compact SUV) — https://www.mitsubishi-motors.ca/en/vehicles/rvr
Prioritize Outlander PHEV but reference others where relevant.

STRATEGIC GOALS: Innovation (S-AWC, connected services, safety tech), Features (adaptive cruise, drive modes), Electrification (Outlander PHEV as Canada's best-selling PHEV SUV; gas models also important), Customer experience (warranty: https://www.mitsubishi-motors.ca/en/owners/warranty), Canadian adventure.

TONE: Confident, innovative, customer-first, approachable. Benefits-focused for Canadian drivers.

CONTENT TYPE:
- Regular blog: 6-7 H2 sections, 1600-2000 words
- Pillar page: 10-12 H2 sections, 3000+ words
- Infer from topic and keyword intent

SECTION STRUCTURE: H2 title, 3-4 questions to answer, specific directive content suggestions, H3s where needed, internal links (mitsubishi-motors.ca only), external links (credible only — NO competitor automakers, NO forums), GEO elements where relevant.

MANDATORY: Legal disclaimer at end linking to https://www.mitsubishi-motors.ca/en/owners/know-your-mitsubishi/owners-manuals. Final section has CTA to relevant vehicle or configure page. Optional sections labeled as optional.

GEO/SEO (where relevant only): comparison tables, bullet checklists, FAQ schema, Key Takeaways or What this covers after intro, definitional language."""
    },
    "Schulich ExecEd": {
        "industry": "Executive Education — Canada",
        "brief": """AUDIENCE: Introspective, growth-oriented, self-learning focused professionals. Looking inward for clarity — not motivation-by-hype.

TONE: Clear, logical, thoughtful. Calm authority. Insight over buzzwords. Explain WHY things matter. No hype, no team-synergy framing.

CONTENT BIAS: Practical meaning, decision clarity, leadership thinking. Judgment, prioritization, sense-making.

CONTENT TYPE: Thought leadership blog, 6-8 H2 sections, 1200-1500 words. Flex based on topic complexity.

SECTION STRUCTURE: H2 title, 3-4 questions to answer, specific directive content suggestions, internal links (execed.schulich.yorku.ca), external links (McKinsey, HBR, ScienceDirect, APA, Frontiers only).

MANDATORY: Key Takeaways box OR What this article covers bullets after intro. Final section positions Schulich ExecEd as learning partner with CTA to specific relevant program.

GEO/SEO (where relevant only): bullet lists for clarity, tables/frameworks for comparisons, synthesis moments, definitional language, FAQ only if high PAA volume."""
    }
}

# ── Session state ────────────────────────────────────────────────────────────
if "clients" not in st.session_state:
    st.session_state.clients = DEFAULT_CLIENTS.copy()
if "outline" not in st.session_state:
    st.session_state.outline = None
if "generated_html" not in st.session_state:
    st.session_state.generated_html = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 NP Digital\n**Blog Outline Generator**")
    st.markdown("---")

    st.markdown("#### Clients")
    for name in list(st.session_state.clients.keys()):
        c = st.session_state.clients[name]
        with st.expander(f"**{name}** · {c['industry']}"):
            new_brief = st.text_area("Brief", value=c["brief"], height=200, key=f"brief_{name}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key=f"save_{name}"):
                    st.session_state.clients[name]["brief"] = new_brief
                    st.success("Saved!")
            with col2:
                if st.button("Delete", key=f"del_{name}"):
                    del st.session_state.clients[name]
                    st.rerun()

    st.markdown("---")
    st.markdown("#### Add client")
    with st.expander("+ New client"):
        new_name = st.text_input("Name", key="new_name")
        new_industry = st.text_input("Industry", key="new_industry")
        new_brief = st.text_area("Brief & guidelines", height=150, key="new_brief")
        if st.button("Add client"):
            if new_name and new_brief:
                st.session_state.clients[new_name] = {"industry": new_industry, "brief": new_brief}
                st.success(f"Added {new_name}!")
                st.rerun()
            else:
                st.warning("Name and brief required.")

# ── Main ─────────────────────────────────────────────────────────────────────
st.markdown('<span class="tag">SEO + GEO Optimized</span>', unsafe_allow_html=True)
st.markdown("# Blog Outline Generator")
st.markdown("Select a client, enter a topic and keyword — Claude handles the rest.")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    client_options = ["— no client —"] + list(st.session_state.clients.keys())
    selected_client = st.selectbox("Client", client_options)

with col2:
    topic = st.text_input("Topic / working title", placeholder="e.g. Towing Capacity Explained: Braked vs Unbraked")

col3, col4 = st.columns(2)
with col3:
    main_kw = st.text_input("Target keyword", placeholder="e.g. braked vs unbraked towing capacity")
with col4:
    notes = st.text_input("Notes (optional)", placeholder="e.g. focus on Outlander PHEV, include warranty link")

if selected_client != "— no client —":
    client = st.session_state.clients[selected_client]
    st.caption(f"📋 **{selected_client}** brief loaded — {client['brief'][:200]}...")

st.markdown("")
generate_btn = st.button("⚡ Generate Outline + Create Google Doc")

# ── Generation ───────────────────────────────────────────────────────────────
def build_prompt(topic, main_kw, notes, client_name, client):
    client_section = ""
    if client:
        # Send a condensed version of the brief to save tokens
        brief_lines = client['brief'].strip().split('\n')
        brief_condensed = '\n'.join(brief_lines[:40])  # first 40 lines
        client_section = f"\nCLIENT: {client_name}\nGUIDELINES:\n{brief_condensed}\n"

    notes_line = f"\nNOTES: {notes}" if notes else ""

    return f"""SEO content strategist at NP Digital. Create a blog outline as JSON only.
{client_section}
TOPIC: {topic}
KEYWORD: {main_kw}{notes_line}

Rules:
- Mitsubishi: 6-7 H2s, 1600-2000 words (pillar: 10-12 H2s, 3000+), Key Takeaways after intro, owner manual disclaimer, CTA to vehicle page, no competitor links
- Schulich: 6-8 H2s, 1200-1500 words, Key Takeaways after intro, academic external links, CTA to specific program
- All: 3 questions per section, 3 specific content suggestions, GEO elements only where valuable
- Keep all string values SHORT (under 120 chars each)
- For topRankingUrls: only use well-known domains you are certain exist (e.g. caa.ca, nhtsa.gov, canada.ca, hbr.org). Use domain only — never fabricate URL paths. If unsure, use the homepage URL only.

Return ONLY this JSON:
{{
  "proposedTitle": "string",
  "contentObjective": "string",
  "url": "/slug",
  "targetWordCount": "string",
  "audience": "string",
  "mainKeyword": "{main_kw}",
  "haloKeywords": ["kw1","kw2","kw3","kw4","kw5"],
  "peopleAlsoAsk": ["q1","q2","q3","q4","q5"],
  "serpFeatureType": "string",
  "serpFeaturePreview": "string",
  "topRankingUrls": [
    {{"url":"domain.com (homepage or known section only — no fabricated paths)","topKeyword":"kw","estTraffic":"2,000","wordCount":"1,800"}},
    {{"url":"domain2.com","topKeyword":"kw","estTraffic":"1,200","wordCount":"2,100"}},
    {{"url":"domain3.com","topKeyword":"kw","estTraffic":"800","wordCount":"1,500"}}
  ],
  "introNote": "string",
  "proposedTitleTag": "string under 60 chars",
  "proposedMetaDescription": "string under 155 chars",
  "disclaimer": "string or null",
  "sections": [
    {{
      "h2": "string",
      "optional": false,
      "questionsToAnswer": ["q1","q2","q3"],
      "contentSuggestion": ["s1","s2","s3"],
      "geoElement": "string or null",
      "internalLinks": ["url1"],
      "externalLinks": ["url1"],
      "ctaUrl": null,
      "ctaCopy": null
    }}
  ]
}}"""


def get_doc_title(client_name, proposed_title):
    """Generate standardized doc title: [Client] New Blog Outline - [Title] - [Month Year]"""
    from datetime import datetime
    month_map = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    now = datetime.now()
    month_year = f"{month_map[now.month]} {now.year}"

    client_prefix_map = {
        "Mitsubishi Motors Canada": "MMSCAN",
        "Schulich ExecEd": "Schulich ExecEd"
    }
    prefix = client_prefix_map.get(client_name, client_name)
    return f"{prefix} New Blog Outline - {proposed_title} - {month_year}"


def build_doc_sections(outline):
    sections = []

    def add(t, text, label=None, value=None):
        if t == "label_value":
            sections.append({"type": t, "label": str(label or ""), "value": str(value or ""), "text": ""})
        else:
            sections.append({"type": t, "text": str(text or "")})

    # Orange H1 title
    add("title", f"Content Outline: {outline.get('proposedTitle','')}")
    add("spacer", "")

    # Metadata fields - label bold, value normal
    add("label_value", "", label="Proposed Title [H1]: ", value=outline.get("proposedTitle",""))
    add("label_value", "", label="Content Objective: ", value=outline.get("contentObjective",""))
    add("label_value", "", label="URL [New Page]: ", value=outline.get("url",""))
    add("label_value", "", label="Target Word Count: ", value=outline.get("targetWordCount",""))
    add("label_value", "", label="Audience: ", value=outline.get("audience",""))
    add("label_value", "", label="Main Keyword: ", value=outline.get("mainKeyword",""))
    add("spacer", "")

    if outline.get("haloKeywords"):
        add("bold", "Halo Keywords:")
        for k in outline["haloKeywords"]:
            add("bullet", k)
        add("spacer", "")

    if outline.get("peopleAlsoAsk"):
        add("bold", "People Also Ask:")
        for q in outline["peopleAlsoAsk"]:
            add("bullet", q)
        add("spacer", "")

    add("bold", "SERP Feature:")
    add("label_value", "", label="Type: ", value=outline.get("serpFeatureType",""))
    add("label_value", "", label="Preview: ", value=outline.get("serpFeaturePreview",""))
    add("spacer", "")

    add("label_value", "", label="Proposed Title Tag: ", value=outline.get("proposedTitleTag",""))
    add("label_value", "", label="Proposed Meta Description: ", value=outline.get("proposedMetaDescription",""))
    add("spacer", "")

    if outline.get("topRankingUrls"):
        add("bold", "Top Ranking URLs:")
        for r in outline["topRankingUrls"]:
            add("normal", f"{r.get('url','')} | {r.get('topKeyword','')} | Est. traffic: {r.get('estTraffic','')} | Word count: {r.get('wordCount','')}")
        add("spacer", "")

    if outline.get("introNote"):
        add("bold", "Intro note:")
        add("normal", outline["introNote"])
        add("spacer", "")

    for i, sec in enumerate(outline.get("sections", [])):
        label = f"{'[Optional] ' if sec.get('optional') else ''}Section {i+1} [H2]: {sec.get('h2','')}"
        add("heading2", label)

        if sec.get("questionsToAnswer"):
            add("bold", "Questions to answer:")
            for q in sec["questionsToAnswer"]:
                add("bullet", q)

        if sec.get("contentSuggestion"):
            add("bold", "Content Suggestion:")
            for s in sec["contentSuggestion"]:
                add("bullet", s)

        geo = sec.get("geoElement")
        if geo and geo != "null" and geo is not None:
            add("bold", "GEO/SEO element:")
            add("normal", geo)

        if sec.get("internalLinks"):
            add("bold", "Internal links:")
            for l in sec["internalLinks"]:
                add("bullet", l)

        if sec.get("externalLinks"):
            add("bold", "External links:")
            for l in sec["externalLinks"]:
                add("bullet", l)

        if sec.get("ctaUrl"):
            add("label_value", "", label="Call to action URL: ", value=sec["ctaUrl"])
            add("label_value", "", label="Call to action copy suggestion: ", value=sec.get("ctaCopy",""))

        add("spacer", "")

    disclaimer = outline.get("disclaimer")
    if disclaimer and disclaimer != "null":
        add("bold", "Legal disclaimer:")
        add("normal", disclaimer)
        add("spacer", "")

    add("normal", "Note that while this outline provides a foundation for the blog, specifics may pivot as needed during the writing phase.")
    return sections


def push_to_docs(script_url, title, sections, client_name=""):
    res = requests.post(script_url, json={"title": title, "sections": sections, "clientName": client_name}, timeout=30)
    return res.json()


if generate_btn:
    if not topic:
        st.error("Please enter a topic.")
    elif not main_kw:
        st.error("Please enter a target keyword.")
    else:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            script_url = st.secrets["APPS_SCRIPT_URL"]
        except Exception:
            st.error("Missing secrets. Add ANTHROPIC_API_KEY and APPS_SCRIPT_URL to your Streamlit secrets.")
            st.stop()

        client = st.session_state.clients.get(selected_client) if selected_client != "— no client —" else None
        client_name = selected_client if selected_client != "— no client —" else ""

        with st.spinner("Generating outline with Claude..."):
            try:
                anthropic_client = anthropic.Anthropic(api_key=api_key)
                message = anthropic_client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=6000,
                    system="You are an expert SEO/GEO content strategist. Respond ONLY with valid JSON. No markdown, no backticks, no explanation before or after the JSON.",
                    messages=[{"role": "user", "content": build_prompt(topic, main_kw, notes, client_name, client)}]
                )
                raw = message.content[0].text.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                # Find the JSON object boundaries
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start != -1 and end > start:
                    raw = raw[start:end]
                outline = json.loads(raw)
                st.session_state.outline = outline
            except Exception as e:
                st.error(f"Generation error: {e}")
                st.stop()

        with st.spinner("Creating Google Doc..."):
            try:
                proposed_title = (outline.get("proposedTitle") or topic)
                doc_title = get_doc_title(client_name, proposed_title)
                sections = build_doc_sections(outline)
                result = push_to_docs(script_url, doc_title, sections)
                if result.get("success"):
                    st.session_state.doc_url = result["url"]
                    st.session_state.doc_title = doc_title
                else:
                    st.error(f"Google Docs error: {result.get('error')}")
                    st.stop()
            except Exception as e:
                st.error(f"Google Docs error: {e}")
                st.stop()

# ── Results ──────────────────────────────────────────────────────────────────
if st.session_state.outline and st.session_state.get("doc_url"):
    outline = st.session_state.outline
    doc_url = st.session_state.doc_url

    st.success(f"✅ Done! [{st.session_state.doc_title}]({doc_url})")
    st.markdown(f"**{outline.get('targetWordCount','')} words · {len(outline.get('sections',[]))} sections · {outline.get('mainKeyword','')}**")

    with st.expander("Preview outline", expanded=True):
        st.markdown(f"### {outline.get('proposedTitle','')}")
        st.markdown(f"**Content Objective:** {outline.get('contentObjective','')}")
        st.markdown(f"**URL:** `{outline.get('url','')}`")
        st.markdown(f"**Word Count:** {outline.get('targetWordCount','')} &nbsp;|&nbsp; **Audience:** {outline.get('audience','')}")

        col_a, col_b = st.columns(2)
        with col_a:
            if outline.get("haloKeywords"):
                st.markdown("**Halo Keywords:**")
                for k in outline["haloKeywords"]:
                    st.markdown(f"- {k}")
        with col_b:
            if outline.get("peopleAlsoAsk"):
                st.markdown("**People Also Ask:**")
                for q in outline["peopleAlsoAsk"][:5]:
                    st.markdown(f"- {q}")

        st.markdown(f"**Title Tag:** {outline.get('proposedTitleTag','')}")
        st.markdown(f"**Meta Description:** {outline.get('proposedMetaDescription','')}")
        st.markdown("---")

        for i, sec in enumerate(outline.get("sections", [])):
            label = f"{'🔵 [Optional] ' if sec.get('optional') else ''}**Section {i+1} — {sec.get('h2','')}**"
            st.markdown(label)
            if sec.get("questionsToAnswer"):
                st.markdown("*Questions to answer:*")
                for q in sec["questionsToAnswer"]:
                    st.markdown(f"  - {q}")
            if sec.get("contentSuggestion"):
                st.markdown("*Content suggestions:*")
                for s in sec["contentSuggestion"]:
                    st.markdown(f"  - {s}")
            geo = sec.get("geoElement")
            if geo and geo != "null":
                st.info(f"🎯 GEO/SEO: {geo}")
            if sec.get("ctaUrl"):
                st.markdown(f"**CTA:** {sec.get('ctaUrl')} — {sec.get('ctaCopy','')}")
            st.markdown("")

        disclaimer = outline.get("disclaimer")
        if disclaimer and disclaimer != "null":
            st.warning(f"⚠️ Legal disclaimer: {disclaimer}")

    st.markdown(f"[Open Google Doc →]({doc_url})")
