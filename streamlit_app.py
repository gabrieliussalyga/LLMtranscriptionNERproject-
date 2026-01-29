import streamlit as st
import asyncio
import json
import os
import sys
import uuid
import streamlit.components.v1 as components

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import get_settings
from backend.services.gemini_extractor import GeminiExtractor
from backend.services.openai_extractor import OpenAIExtractor
from backend.models.transcript import TranscriptInput

# Page configuration
st.set_page_config(
    page_title="Medical NER Extraction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-size: 14px;
    }
    .stChatMessage {
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    .stChatMessage p {
        font-size: 0.9rem;
    }
    
    /* Highlight style */
    .highlighted-segment {
        background-color: #fff9c4;
        border-left: 4px solid #fbc02d;
        padding-left: 8px;
        scroll-margin-top: 200px; /* Offset for sticky headers */
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    
    /* Small button for highlighting */
    div[data-testid="column"] button {
        font-size: 0.7rem;
        padding: 0rem 0.5rem;
        min-height: 0px;
        height: 24px;
    }

    /* Clickable statement card styling - target buttons inside expanders */
    div[data-testid="stExpander"] div[data-testid="stButton"] > button {
        background-color: #f8f9fa !important;
        border: 1px solid #e0e0e0 !important;
        border-left: 3px solid #4CAF50 !important;
        border-radius: 3px !important;
        padding: 3px 8px !important;
        margin-bottom: 2px !important;
        font-size: 0.8rem !important;
        line-height: 1.2 !important;
        text-align: left !important;
        width: auto !important;
        color: #333 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        height: auto !important;
        min-height: 0 !important;
        white-space: normal !important;
    }
    div[data-testid="stExpander"] div[data-testid="stButton"] > button:hover {
        background-color: #e8f5e9 !important;
        border-left-color: #2E7D32 !important;
    }
    div[data-testid="stExpander"] div[data-testid="stButton"] > button:active {
        background-color: #c8e6c9 !important;
    }
    div[data-testid="stExpander"] div[data-testid="stButton"] {
        margin: 8px 6px !important;
        padding: 0 !important;
        display: inline-block !important;
        vertical-align: top !important;
    }

    /* Tighter expander styling */
    div[data-testid="stExpander"] details {
        margin-bottom: 2px !important;
    }
    div[data-testid="stExpander"] summary {
        padding: 4px 8px !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        padding: 4px 8px !important;
    }
    /* Force all nested divs in expander to be inline for chip-like layout */
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] > div,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] > div > div,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] > div > div > div,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] > div > div > div > div {
        display: inline !important;
        width: auto !important;
    }
    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
        display: inline !important;
        gap: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Load settings
settings = get_settings()

def get_extractor():
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            st.error("OPENAI_API_KEY not configured in .env file")
            return None
        return OpenAIExtractor(
            api_key=settings.openai_api_key,
            model_name=settings.openai_model
        )
    else:
        if not settings.google_api_key:
            st.error("GOOGLE_API_KEY not configured in .env file")
            return None
        return GeminiExtractor(
            api_key=settings.google_api_key,
            model_name=settings.gemini_model
        )

# Helper for highlighting
def highlight_segments(segment_ids):
    # Set segments
    st.session_state.highlighted_segments = set(segment_ids or [])
    # Generate a new unique ID for the scroll target to force fresh JS execution
    st.session_state.scroll_id = f"scroll-target-{uuid.uuid4().hex[:8]}"

# Initialize session state
if "transcript_text" not in st.session_state:
    try:
        with open("full_test_request.json", "r") as f:
            st.session_state.transcript_text = f.read()
    except:
        st.session_state.transcript_text = ""

if "extraction_result" not in st.session_state:
    st.session_state.extraction_result = None
if "transcript_data" not in st.session_state:
    # Auto-load on start
    try:
        if st.session_state.transcript_text:
            data = json.loads(st.session_state.transcript_text)
            st.session_state.transcript_data = data.get("transcript", data)
    except:
        st.session_state.transcript_data = None

if "highlighted_segments" not in st.session_state:
    st.session_state.highlighted_segments = set()
if "scroll_id" not in st.session_state:
    st.session_state.scroll_id = "scroll-target-init"
if "expanders_state" not in st.session_state:
    st.session_state.expanders_state = True  # True = expanded, False = collapsed
if "analysis_in_progress" not in st.session_state:
    st.session_state.analysis_in_progress = False

# Header
st.title("🏥 Medicininių Esybių Išgavimas")

# Layout
left_col, right_col = st.columns([4, 5])

# --- LEFT COLUMN: Input & Transcript Viewer ---
with left_col:
    # Input Section (Always Collapsed initially if data exists)
    with st.expander("📝 Įvestis / Redagavimas", expanded=not st.session_state.transcript_data):
        input_text = st.text_area(
            "JSON",
            value=st.session_state.transcript_text,
            height=200,
            key="transcript_text_area",
            label_visibility="collapsed"
        )
        
        # Combined Load & Extract
        if st.button("Užkrauti ir Analizuoti", type="primary", use_container_width=True):
            try:
                input_json = json.loads(input_text)
                st.session_state.transcript_data = input_json.get("transcript", input_json)
                st.session_state.extraction_result = None # Clear old results
                st.session_state.highlighted_segments = set()
                
                # Trigger extraction immediately
                extractor = get_extractor()
                if extractor:
                    with st.spinner("Analizuojama..."):
                        transcript_input = TranscriptInput(transcript=st.session_state.transcript_data)
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(extractor.extract(transcript_input))
                        loop.close()
                        st.session_state.extraction_result = result
                st.rerun()
                
            except json.JSONDecodeError:
                st.error("Neteisingas JSON formatas")
            except Exception as e:
                st.error(f"Klaida: {str(e)}")

    # Transcript Viewer
    if st.session_state.transcript_data:
        st.markdown("### Transkripcija")
        container = st.container(height=650)
        with container:
            first_highlight_found = False
            current_scroll_id = st.session_state.scroll_id
            
            for i, segment in enumerate(st.session_state.transcript_data):
                speaker = segment.get("speaker", "Unknown")
                text = segment.get("text", "")
                time = segment.get("time", "")
                
                is_highlighted = i in st.session_state.highlighted_segments
                
                # Visuals
                if "gydytoj" in speaker.lower():
                    avatar = "🧑‍⚕️"
                else:
                    avatar = "👤"
                
                # Apply highlight style and ID
                if is_highlighted:
                    # Only assign the unique ID to the FIRST highlighted segment
                    div_props = ""
                    if not first_highlight_found:
                        div_props = f'id="{current_scroll_id}"'
                        first_highlight_found = True
                    
                    st.markdown(f"""
                    <div {div_props} class="highlighted-segment" style="margin-bottom: 10px;">
                        <span style='font-weight:bold'>{speaker}</span> <span style='color:gray; font-size:0.75em'>[{time}]</span><br>
                        {text}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    with st.chat_message(name=speaker, avatar=avatar):
                        st.write(f"<span style='color:#666; font-size:0.75em'>[{time}]</span> {text}", unsafe_allow_html=True)
            
            # Inject JS if we have a target
            if first_highlight_found:
                components.html(
                    f"""
                    <script>
                        var attempts = 0;
                        var targetId = '{current_scroll_id}';
                        function scroll() {{
                            const element = window.parent.document.getElementById(targetId);
                            if (element) {{
                                element.scrollIntoView({{behavior: 'smooth', block: 'center', inline: 'nearest'}});
                                console.log("Scrolled to " + targetId);
                                return true;
                            }}
                            return false;
                        }}
                        
                        var interval = setInterval(function() {{
                            if (scroll()) {{
                                clearInterval(interval);
                            }}
                            attempts++;
                            if (attempts > 50) {{ 
                                clearInterval(interval);
                            }}
                        }}, 100);
                    </script>
                    """,
                    height=0,
                    width=0
                )

# --- RIGHT COLUMN: Results ---
with right_col:
    st.markdown("### Išgauti Duomenys")
    
    result = st.session_state.extraction_result
    
    if result:
        doc = result.document

        # Helper to render a clickable statement card
        def render_statement_card(statement, segments, card_index):
            if st.button(statement, key=f"stmt_{card_index}_{st.session_state.scroll_id[-4:]}"):
                if segments:
                    highlight_segments(segments)
                    st.rerun()

        # Expand/Collapse All buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        with btn_col1:
            if st.button("➕ Išskleisti", use_container_width=True):
                st.session_state.expanders_state = True
                st.rerun()
        with btn_col2:
            if st.button("➖ Sutraukti", use_container_width=True):
                st.session_state.expanders_state = False
                st.rerun()

        exp_state = st.session_state.expanders_state

        # Create scrollable container for all categories
        results_container = st.container(height=620)
        with results_container:

            # --- VIZITAS IR RODIKLIAI ---
            with st.expander("📋 Vizitas ir Rodikliai", expanded=exp_state):
                col1, col2 = st.columns(2)
                with col1:
                    if doc.visit:
                        st.markdown("**Vizito Informacija**")
                        st.write(f"📅 {doc.visit.date or '-'}")
                        st.write(f"🕒 {doc.visit.time or '-'}")
                        st.write(f"👨‍⚕️ {doc.visit.physician or '-'}")

                with col2:
                    if doc.body_measurements:
                        st.markdown("**Kūno Matavimai**")
                        bm = doc.body_measurements
                        if bm.weight: st.write(f"⚖️ {bm.weight} kg")
                        if bm.height: st.write(f"📏 {bm.height} cm")
                        if bm.bmi: st.write(f"📊 KMI: {bm.bmi}")

                if doc.vital_signs and doc.vital_signs.items:
                    st.markdown("**Gyvybiniai Rodikliai**")
                    for i, item in enumerate(doc.vital_signs.items):
                        render_statement_card(f"{item.name} {item.value}", item.source_segments, f"vital_{i}")

            # --- NUSISKUNDIMAI (ANAMNEZĖ) ---
            with st.expander("🗣️ Nusiskundimai (Anamnezė)", expanded=exp_state):
                if doc.clinical_notes and doc.clinical_notes.complaints_anamnesis:
                    for i, item in enumerate(doc.clinical_notes.complaints_anamnesis):
                        render_statement_card(item.statement, item.source_segments, f"anamneze_{i}")
                else:
                    st.info("Nėra duomenų.")

            # --- OBJEKTYVI BŪKLĖ ---
            with st.expander("🔬 Objektyvi Būklė", expanded=exp_state):
                if doc.clinical_notes and doc.clinical_notes.objective_condition:
                    for i, item in enumerate(doc.clinical_notes.objective_condition):
                        render_statement_card(item.statement, item.source_segments, f"objektyvi_{i}")
                else:
                    st.info("Nėra duomenų.")

            # --- DIAGNOZĖS ---
            with st.expander("🏥 Diagnozės", expanded=exp_state):
                if doc.diagnosis and doc.diagnosis.items:
                    for i, item in enumerate(doc.diagnosis.items):
                        certainty = {"+": "Patvirtinta", "-": "Atmesta", "0": "Įtariama"}.get(item.diagnosis_certainty, item.diagnosis_certainty)
                        code_part = f"[{item.diagnosis_code}] " if item.diagnosis_code else ""
                        render_statement_card(f"{code_part}{item.diagnosis} ({certainty})", item.source_segments, f"diag_{i}")
                else:
                    st.info("Nėra duomenų.")

            # --- GYDYMAS ---
            with st.expander("💊 Gydymas", expanded=exp_state):
                if doc.treatment and doc.treatment.items:
                    for i, item in enumerate(doc.treatment.items):
                        render_statement_card(item.description, item.source_segments, f"gydymas_{i}")
                else:
                    st.info("Nėra duomenų.")

            # --- TYRIMŲ PLANAS ---
            with st.expander("📝 Tyrimų Planas", expanded=exp_state):
                if doc.clinical_notes and doc.clinical_notes.tests_consultations_plan:
                    for i, item in enumerate(doc.clinical_notes.tests_consultations_plan):
                        render_statement_card(item.statement, item.source_segments, f"planas_{i}")
                else:
                    st.info("Nėra duomenų.")

            # --- ALERGIJOS IR KITA ---
            with st.expander("⚠️ Alergijos ir Kita", expanded=exp_state):
                if doc.allergies:
                    st.markdown("**Alergijos**")
                    for i, allergy in enumerate(doc.allergies):
                        render_statement_card(f"{allergy.description}", allergy.source_segments, f"allergy_{i}")

                if doc.referral:
                    st.markdown("**Siuntimas**")
                    r = doc.referral
                    st.write(f"Gydytojas: {r.referring_physician}")
                    st.write(f"Įstaiga: {r.referring_institution}")
                    st.write(f"Diagnozė: {r.referral_diagnosis}")

                if doc.certificates:
                    st.markdown("**Pažymos**")
                    c = doc.certificates
                    if c.disability_certificate:
                        st.warning(f"Nedarbingumas: {c.disability_start_date} - {c.disability_end_date}")

                if not doc.allergies and not doc.referral and not doc.certificates:
                    st.info("Nėra duomenų.")

    elif st.session_state.transcript_data:
        is_analyzing = st.session_state.analysis_in_progress
        btn_label = "⏳ Analizuojama..." if is_analyzing else "🚀 Pradėti Analizę"

        if st.button(btn_label, type="primary", use_container_width=True, disabled=is_analyzing):
            st.session_state.analysis_in_progress = True
            st.rerun()

        if is_analyzing:
            extractor = get_extractor()
            if extractor:
                with st.spinner("Analizuojama..."):
                    try:
                        transcript_input = TranscriptInput(transcript=st.session_state.transcript_data)
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(extractor.extract(transcript_input))
                        loop.close()
                        st.session_state.extraction_result = result
                    except Exception as e:
                        st.error(f"Klaida: {str(e)}")
                    finally:
                        st.session_state.analysis_in_progress = False
                        st.rerun()
    else:
        st.write("👈 Įkelkite duomenis kairėje.")
