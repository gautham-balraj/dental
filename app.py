import streamlit as st
import io
import time
from PIL import Image
from google import genai
from google.genai import types

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dental Radiography Analysis Tool · Periodontal Radiograph Analyser",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Global CSS – clinical dark theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #0b0f14;
    --surface:   #111720;
    --surface2:  #161d27;
    --border:    #1e2d3d;
    --accent:    #00c2ff;
    --accent2:   #00ffd0;
    --text:      #dce8f5;
    --muted:     #5a7a96;
    --danger:    #ff4f6b;
    --ok:        #00e396;
    --radius:    12px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }

/* ── Typography ── */
h1, h2, h3 { font-family: 'DM Sans', sans-serif; font-weight: 600; letter-spacing: -0.02em; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #0d1f35 0%, #061422 50%, #091929 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.4rem 2.8rem 2rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(0,194,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-tag {
    display: inline-block;
    background: rgba(0,194,255,0.12);
    color: var(--accent);
    border: 1px solid rgba(0,194,255,0.3);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 100px;
    margin-bottom: 0.8rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #fff;
    margin: 0 0 0.4rem;
    line-height: 1.15;
}
.hero p {
    color: var(--muted);
    font-size: 0.95rem;
    margin: 0;
    max-width: 560px;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem;
    margin-bottom: 1.2rem;
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Stat pills ── */
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1rem; }
.stat-pill {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: var(--muted);
}
.stat-pill span { color: var(--text); font-weight: 600; display: block; font-size: 1rem; }

/* ── Step badges ── */
.steps { display: flex; flex-direction: column; gap: 10px; }
.step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 0.88rem;
    color: #7a9bb8;
}
.step-num {
    width: 24px; height: 24px;
    background: rgba(0,194,255,0.1);
    border: 1px solid rgba(0,194,255,0.3);
    border-radius: 50%;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ── Feature grid ── */
.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.feature-item {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 0.82rem;
    color: #7a9bb8;
}
.feature-item strong { color: var(--text); display: block; margin-bottom: 2px; font-size: 0.85rem; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0071a8 0%, #005b87 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
}

/* ── Result markdown ── */
.result-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.8rem;
}
.result-box h2, .result-box h3 {
    color: var(--accent) !important;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-top: 1.4rem;
}
.result-box h4 { color: var(--accent2) !important; margin-top: 1rem; }
.result-box ul { padding-left: 1.2rem; }
.result-box li { margin-bottom: 4px; color: var(--text); line-height: 1.65; }
.result-box strong { color: #fff; }
.result-box code {
    background: rgba(0,194,255,0.08);
    color: var(--accent2);
    border-radius: 4px;
    padding: 1px 5px;
    font-family: 'DM Mono', monospace;
    font-size: 0.85em;
}

/* ── Status badges ── */
.badge-ok   { background: rgba(0,227,150,0.12); color: var(--ok);    border: 1px solid rgba(0,227,150,0.3); border-radius:6px; padding: 3px 10px; font-size:0.78rem; font-weight:600; }
.badge-warn { background: rgba(255,196,0,0.12);  color: #ffc400;      border: 1px solid rgba(255,196,0,0.3); border-radius:6px; padding: 3px 10px; font-size:0.78rem; font-weight:600; }
.badge-err  { background: rgba(255,79,107,0.12); color: var(--danger); border: 1px solid rgba(255,79,107,0.3); border-radius:6px; padding: 3px 10px; font-size:0.78rem; font-weight:600; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}

/* ── Spinner text ── */
[data-testid="stSpinner"] p { color: var(--accent) !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: rgba(0,255,208,0.08) !important;
    border: 1px solid rgba(0,255,208,0.3) !important;
    color: var(--accent2) !important;
    font-size: 0.85rem !important;
}

/* ── Image caption ── */
[data-testid="caption"] { color: var(--muted) !important; font-size: 0.78rem !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
API_KEY = st.secrets["API_KEY"]
MAX_RETRIES = 3
RETRY_DELAY = 4  # seconds between retries

ANALYSIS_PROMPT = """
You are a board-certified specialist in dental radiology and periodontology with over 20 years of clinical and academic experience. 
Perform a comprehensive, structured radiographic interpretation of the provided dental image. 
Your report must follow the exact schema below — do NOT omit any heading, even if findings are absent (write "Not detected" or "Not applicable").
Use precise clinical language, include quantitative estimates wherever radiographically derivable, and flag any uncertainty with "(radiographic estimate)" or "(cannot be confirmed without clinical data)".

---

##  Dental Radiography Analysis Tool — PERIODONTAL RADIOGRAPHIC REPORT

### SECTION 1 · Bone Level Measurements

#### 1A · Alveolar Bone Height (relative to CEJ)
- List each assessed region (maxillary anterior, maxillary posterior, mandibular anterior, mandibular posterior) with estimated crestal bone position in mm from CEJ.
- Normal reference: ≤2 mm from CEJ.

#### 1B · Pattern & Extent of Bone Loss
- Characterise as horizontal, vertical (angular), or mixed.
- Specify generalised (>30% of teeth) vs localised (<30%), and mild (<15%), moderate (15–30%), or severe (>30%) bone loss.

#### 1C · Estimated Percentage Bone Loss
- Per tooth or per site where measurable.
- Use the formula: (distance from CEJ to bone crest ÷ root length) × 100.

#### 1D · Comparative Arch / Quadrant Analysis
- Summarise asymmetries between left/right or maxilla/mandible.

---

### SECTION 2 · Furcation Involvement (Molars)

- For each molar assess furcation status:
  - **Grade I** — early involvement (<3 mm horizontal probe depth equivalent)
  - **Grade II** — partial involvement (>3 mm but not through-and-through)
  - **Grade III** — through-and-through involvement
- Note radiographic visibility limitations.

---

### SECTION 3 · Periodontal Ligament (PDL) Space Analysis

- Normal PDL width: 0.15–0.38 mm.
- Flag any widening and its probable aetiology (occlusal trauma, mobility, pathology).
- Assess uniformity around each root assessed.

---

### SECTION 4 · Calculus Detection

- Note location (supragingival / subgingival) and teeth involved.
- Describe extent: trace, moderate, or heavy.
- Correlate with adjacent bone loss where evident.

---

### SECTION 5 · Crestal Bone Morphology

- Describe interproximal crestal contour per region:
  - Sharp & well-defined (healthy)
  - Blunted / flattened (early disease)
  - Irregular / saucerised (active or past disease)
- Note any crestal radiolucency suggestive of inflammation.

---

### SECTION 6 · Tooth-Specific Findings

For each significantly affected tooth:
| Tooth | Finding | Clinical Implication |
|-------|---------|---------------------|
| (use FDI or Universal numbering) | ... | ... |

Include:
- Predicted mobility based on bone support
- Pathologic migration or tipping
- Root proximity / divergence / dilacerations
- Crown-to-root ratio assessment

---

### SECTION 7 · Periapical & Endodontic Pathologies

- Describe periapical radiolucencies (size, shape, margins, associated tooth).
- Identify probable endo-perio lesion if applicable.
- Note internal/external root resorption.
- Assess apical status of root-treated teeth.

---

### SECTION 8 · Implant Analysis (if present)

- Identify implant type/system if recognisable.
- Measure marginal bone loss around implant (distance from implant shoulder to bone crest, mesial and distal).
- Grade peri-implantitis risk:
  - Early: <2 mm bone loss + BOP equivalent
  - Moderate: 2–4 mm bone loss
  - Advanced: >4 mm bone loss or thread exposure
- Note any implant angulation or crown issues.

---

### SECTION 9 · Additional & Incidental Findings

- Periodontal cysts, dentigerous cysts, or other jaw pathology.
- Anatomic variants (tori, dense bone islands, root anomalies).
- Restorations: overhangs, open contacts, faulty margins contributing to disease.
- Imaging artefacts or exposure quality notes.

---

### SECTION 10 · Summary & Clinical Prioritisation

Provide a concise prioritised action list:

**🔴 Urgent (within 2 weeks):** ...  
**🟡 Soon (1–3 months):** ...  
**🟢 Routine (3–6 months recall):** ...

Include an overall Periodontal Staging & Grading estimate per the 2017 World Workshop classification (Stage I–IV, Grade A–C) if sufficient data is visible.

---

*Disclaimer: This is an AI-assisted radiographic interpretation for clinical decision support only. All findings must be correlated with clinical examination, probing data, and patient history before any treatment decision is made.*
"""

# ──────────────────────────────────────────────
# API call with retry
# ──────────────────────────────────────────────
def analyze_dental_image(image_bytes: bytes, mime_type: str) -> tuple[str, str]:
    """
    Returns (result_text, status) where status is 'ok' | 'error'.
    Retries up to MAX_RETRIES times on resource-exhaustion or transient errors.
    """
    last_error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ANALYSIS_PROMPT,
                ],
            )
            return response.text, "ok"
        except Exception as e:
            last_error = str(e)
            err_lower = last_error.lower()
            is_retryable = any(k in err_lower for k in [
                "resource_exhausted", "quota", "rate limit", "429",
                "503", "unavailable", "timeout", "internal",
            ])
            if is_retryable and attempt < MAX_RETRIES:
                st.warning(
                    f"⚠️ API quota / rate-limit hit (attempt {attempt}/{MAX_RETRIES}). "
                    f"Retrying in {RETRY_DELAY}s…"
                )
                time.sleep(RETRY_DELAY)
            else:
                break
    return f"**Analysis failed after {MAX_RETRIES} attempts.**\n\n`{last_error}`", "error"

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.4rem'>
        <div style='font-size:1.5rem'>🦷</div>
        <div style='font-weight:700;font-size:1.05rem;color:#dce8f5'>Dental Radiography Analysis Tool</div>
        <div style='font-size:0.75rem;color:#5a7a96'>Periodontal Radiograph Analyser</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="steps">
        <div class="step"><div class="step-num">1</div><div>Upload a dental X-ray (JPG / PNG)</div></div>
        <div class="step"><div class="step-num">2</div><div>Click <b style='color:#dce8f5'>Analyse Radiograph</b></div></div>
        <div class="step"><div class="step-num">3</div><div>Review the 10-section structured report</div></div>
        <div class="step"><div class="step-num">4</div><div>Download the Markdown report</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#5a7a96;line-height:1.6'>
    ⚠️ <b style='color:#7a9bb8'>Disclaimer</b><br>
    This tool is for educational & clinical decision-support purposes only. 
    All findings must be correlated with clinical examination before treatment.
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Hero header
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">AI · Periodontics · Radiology</div>
    <h1>Dental Radiography Analysis Tool</h1>
    <p>Advanced periodontal radiograph interpretation — 10 structured sections, quantitative bone-level estimates, staging & grading, and clinical prioritisation.</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_status" not in st.session_state:
    st.session_state.analysis_status = None

# ──────────────────────────────────────────────
# Layout: left panel (upload) | right panel (results)
# ──────────────────────────────────────────────
left, right = st.columns([1, 1.35], gap="large")

# ── LEFT PANEL ──────────────────────────────
with left:
    st.markdown('<div class="card-title">📂 Upload Radiograph</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drag & drop or browse",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if uploaded_file:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        w, h = image.size
        st.image(image, caption=f"{uploaded_file.name}  ·  {w}×{h}px", use_column_width=True)

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        # Stat pills
        size_kb = len(uploaded_file.getvalue()) // 1024
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-pill"><span>{w}×{h}</span>Resolution</div>
            <div class="stat-pill"><span>{size_kb} KB</span>File size</div>
            <div class="stat-pill"><span>{uploaded_file.type.split('/')[1].upper()}</span>Format</div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns([2, 1])
        with col_a:
            analyse_clicked = st.button("🔍 Analyse Radiograph", type="primary", use_container_width=True)
        with col_b:
            clear_clicked = st.button("🗑 Clear", type="secondary", use_container_width=True)

        if clear_clicked:
            st.session_state.analysis_result = None
            st.session_state.analysis_status = None
            st.rerun()

        if analyse_clicked:
            with st.spinner("Analysing radiograph — this may take up to 60 seconds…"):
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()

                # MIME detection
                ft = uploaded_file.type
                if ft in ("image/jpeg", "image/png"):
                    mime_type = ft
                elif ft == "image/jpg":
                    mime_type = "image/jpeg"
                else:
                    ext = uploaded_file.name.lower()
                    mime_type = "image/png" if ext.endswith(".png") else "image/jpeg"

                result, status = analyze_dental_image(image_bytes, mime_type)
                st.session_state.analysis_result = result
                st.session_state.analysis_status = status

            if status == "ok":
                st.success("✅ Analysis complete — see report →")
            else:
                st.error("❌ Analysis failed. See error details in the report panel.")

    else:
        # Feature preview when no image uploaded
        st.markdown("""
        <div style='color:#5a7a96;font-size:0.88rem;margin-bottom:1.2rem'>
        Upload any dental periapical, bitewing, or panoramic radiograph to generate a structured 10-section periodontal report.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-grid">
            <div class="feature-item"><strong>🦴 Bone Levels</strong>CEJ distances, % loss, arch comparison</div>
            <div class="feature-item"><strong>🔱 Furcation</strong>Grade I–III classification per molar</div>
            <div class="feature-item"><strong>📏 PDL Space</strong>Widening, uniformity, trauma signs</div>
            <div class="feature-item"><strong>🪨 Calculus</strong>Location, extent, subgingival deposits</div>
            <div class="feature-item"><strong>🔬 Periapical</strong>Abscesses, endo-perio lesions</div>
            <div class="feature-item"><strong>🔩 Implants</strong>Marginal bone loss, peri-implantitis</div>
            <div class="feature-item"><strong>📋 Staging</strong>2017 World Workshop I–IV / A–C</div>
            <div class="feature-item"><strong>🎯 Priorities</strong>Urgent / Soon / Routine action list</div>
        </div>
        """, unsafe_allow_html=True)

# ── RIGHT PANEL ──────────────────────────────
with right:
    st.markdown('<div class="card-title">📋 Radiographic Report</div>', unsafe_allow_html=True)

    if st.session_state.analysis_result:
        status = st.session_state.analysis_status

        # Status badge
        if status == "ok":
            st.markdown('<span class="badge-ok">● Report ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-err">● Analysis failed</span>', unsafe_allow_html=True)

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        # Render report
        st.markdown(
            f'<div class="result-box">{st.session_state.analysis_result}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        if status == "ok":
            st.download_button(
                label="📄 Download Report (.md)",
                data=st.session_state.analysis_result,
                file_name="dentoscan_periodontal_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
    else:
        st.markdown("""
        <div style='
            height: 320px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--surface);
            border: 1px dashed var(--border);
            border-radius: var(--radius);
            color: var(--muted);
            font-size: 0.9rem;
            gap: 12px;
            text-align: center;
            padding: 2rem;
        '>
            <div style='font-size:2.4rem'>🦷</div>
            <div style='font-weight:600;color:#7a9bb8'>Report will appear here</div>
            <div style='font-size:0.82rem;max-width:280px;line-height:1.6'>
                Upload a radiograph and click <b>Analyse Radiograph</b> to generate your structured 10-section periodontal report.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#2e4a62;font-size:0.75rem;padding:0.5rem 0 1rem'>
    Dental Radiography Analysis Tool · Powered by Gemini 2.5 Flash · For clinical decision-support only · Not a substitute for professional diagnosis
</div>
""", unsafe_allow_html=True)
