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
from backend.schemas.e025_flat import load_document_schema, SCHEMA_FILE_PATH

# Page configuration
st.set_page_config(
    page_title="Medical NER Extraction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple login gate
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        valid_user = os.environ.get("APP_USERNAME", "admin")
        valid_pass = os.environ.get("APP_PASSWORD", "")
        if username == valid_user and password == valid_pass:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

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

# --- Sidebar: Schema Viewer ---
with st.sidebar:
    st.header("Schema")
    if st.button("Peržiūrėti schemą", use_container_width=True):
        st.session_state.show_schema = True

    if st.session_state.get("show_schema", False):
        try:
            schema = load_document_schema()
            schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
            st.code(schema_json, language="json")
            st.caption(f"Failas: {SCHEMA_FILE_PATH}")
            if st.button("Uždaryti"):
                st.session_state.show_schema = False
                st.rerun()
        except Exception as e:
            st.error(f"Nepavyko įkelti schemos: {e}")


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
        else:
            st.session_state.transcript_data = None
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
# Dynamic UI based on schema
with right_col:
    st.markdown("### Išgauti Duomenys")

    result = st.session_state.extraction_result

    # Load current schema to determine which fields exist
    current_schema = load_document_schema()
    schema_fields = set(current_schema.get("properties", {}).keys())

    if result:
        doc = result.get("document", {})
        refs = result.get("references", [])

        # Build reference lookup: (field_name, value) -> source_segments
        ref_lookup = {}
        for ref in refs:
            key = f"{ref['field_name']}::{ref['value']}"
            ref_lookup[key] = ref["source_segments"]

        def get_segments(field_name, value):
            return ref_lookup.get(f"{field_name}::{value}", [])

        def render_statement_card(statement, segments, card_index):
            if st.button(statement, key=f"stmt_{card_index}_{st.session_state.scroll_id[-4:]}"):
                if segments:
                    highlight_segments(segments)
                    st.rerun()

        def render_statements(field_name, card_prefix):
            if field_name not in schema_fields:
                return False
            items = doc.get(field_name) or []
            if items:
                for i, item in enumerate(items):
                    stmt = item.get("statement", "") if isinstance(item, dict) else str(item)
                    segs = get_segments(field_name, stmt)
                    render_statement_card(stmt, segs, f"{card_prefix}_{i}")
                return True
            return False

        def render_scalar(label, field_name, value, unit=""):
            if field_name not in schema_fields:
                return
            if value is not None:
                display = f"{value}{unit}"
                segs = get_segments(field_name, str(value))
                render_statement_card(f"{label}: {display}", segs, f"scalar_{field_name}")
            else:
                st.caption(f"{label}: -")

        def render_bool(label, field_name):
            if field_name not in schema_fields:
                return
            val = doc.get(field_name)
            if val is not None:
                render_statement_card(
                    f"{label}: {'Taip' if val else 'Ne'}",
                    get_segments(field_name, str(val)), f"bool_{field_name}"
                )
            else:
                st.caption(f"{label}: -")

        # Expand/Collapse buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        with btn_col1:
            if st.button("+ Išskleisti", use_container_width=True):
                st.session_state.expanders_state = True
                st.rerun()
        with btn_col2:
            if st.button("- Sutraukti", use_container_width=True):
                st.session_state.expanders_state = False
                st.rerun()

        exp_state = st.session_state.expanders_state

        # --- UI GROUP CONFIGURATION ---
        # Each group: (title, emoji, list of (field_name, label, unit_or_type))
        # Types: "statements", "scalar", "bool", "allergies", "vaccinations"
        UI_GROUPS = [
            ("Vizito Informacija", "📋", [
                ("date", "Data", "scalar", ""),
                ("time", "Laikas", "scalar", ""),
                ("status", "Būsena", "scalar", ""),
                ("help_type", "Pagalbos tipas", "scalar", ""),
                ("consultation_type", "Konsultacijos tipas", "scalar", ""),
                ("physician", "Gydytojas", "statements", ""),
                ("service_method", "Aptarnavimo ypatumai", "statements", ""),
                ("record_number", "Įrašo numeris", "statements", ""),
            ]),
            ("Siuntimas", "📨", [
                ("arrived_with_referral", "Atvyko su siuntimu", "bool", ""),
                ("referring_institution", "Siuntusi įstaiga", "statements", ""),
                ("referring_physician", "Siuntęs gydytojas", "statements", ""),
                ("referral_diagnosis", "Siuntimo diagnozė", "statements", ""),
            ]),
            ("GMP", "🚑", [
                ("arrived_by_ambulance", "Atvežtas GMP", "bool", ""),
                ("ambulance_institution", "GMP įstaiga", "statements", ""),
                ("ambulance_diagnosis", "GMP diagnozė", "statements", ""),
            ]),
            ("Nusiskundimai (Anamnezė)", "🗣️", [
                ("complaints_anamnesis", None, "statements", ""),
            ]),
            ("Objektyvi Būklė", "🔬", [
                ("objective_condition", None, "statements", ""),
            ]),
            ("Gyvybiniai Rodikliai", "❤️", [
                ("systolic_bp", "Sistolinis", "scalar", " mmHg"),
                ("diastolic_bp", "Diastolinis", "scalar", " mmHg"),
                ("pulse", "Pulsas", "scalar", " k/min"),
                ("breathing_rate", "Kvėpavimo dažnis", "scalar", " k/min"),
                ("saturation", "Saturacija", "scalar", "%"),
                ("temperature", "Temperatūra", "scalar", "°C"),
                ("alcohol_level", "Alkoholis", "scalar", "‰"),
            ]),
            ("Kūno Matavimai", "📏", [
                ("weight", "Svoris", "scalar", " kg"),
                ("height", "Ūgis", "scalar", " cm"),
                ("bmi", "KMI", "scalar", ""),
                ("chest_circumference", "Krūtinės apimtis", "scalar", " cm"),
                ("hip_circumference", "Klubų apimtis", "scalar", " cm"),
                ("waist_circumference", "Juosmens apimtis", "scalar", " cm"),
                ("head_circumference", "Galvos apimtis", "scalar", " cm"),
            ]),
            ("Diagnozės", "🏥", [
                ("diagnosis", "Diagnozė", "statements", ""),
                ("diagnosis_code", "Diagnozės kodas", "scalar", ""),
                ("diagnosis_certainty", "Diagnozės tikrumas", "scalar", ""),
                ("clinical_diagnosis", "Klinikinė diagnozė", "statements", ""),
            ]),
            ("Medikamentinis Gydymas", "💊", [
                ("medication_treatment", None, "statements", ""),
            ]),
            ("Nemedikamentinis Gydymas", "🏥", [
                ("non_medication_treatment", None, "statements", ""),
            ]),
            ("Receptai", "📋", [
                ("prescriptions", None, "statements", ""),
            ]),
            ("Siuntimai", "📤", [
                ("referrals", None, "statements", ""),
            ]),
            ("Rekomendacijos", "💡", [
                ("recommendations", None, "statements", ""),
            ]),
            ("Tyrimų Planas", "📝", [
                ("tests_consultations_plan", None, "statements", ""),
            ]),
            ("Atlikti Tyrimai", "🔬", [
                ("performed_tests_consultations", None, "statements", ""),
            ]),
            ("Būklė Išrašant", "🏠", [
                ("condition_on_discharge", None, "statements", ""),
            ]),
            ("Alergijos", "⚠️", [
                ("allergies", None, "allergies", ""),
            ]),
            ("Skiepai", "💉", [
                ("vaccinations", None, "vaccinations", ""),
            ]),
            ("Pažymos", "📄", [
                ("disability_certificate", "Nedarbingumo pažymėjimas", "bool", ""),
                ("maternity_certificate", "Nėštumo/gimdymo pažymėjimas", "bool", ""),
                ("medical_certificate", "Medicininė pažyma", "bool", ""),
                ("disability_number", "Pažymėjimo numeris", "statements", ""),
                ("disability_start_date", "Nedarbingumas nuo", "scalar", ""),
                ("disability_end_date", "Nedarbingumas iki", "scalar", ""),
                ("disability_description", "Nedarbingumo aprašymas", "statements", ""),
            ]),
            ("Apribojimai", "🚫", [
                ("cannot_drive", "Draudimas vairuoti", "bool", ""),
                ("cannot_drive_date", "Draudimo vairuoti data", "scalar", ""),
                ("cannot_use_weapon", "Draudimas naudoti ginklą", "bool", ""),
            ]),
            ("Pastabos", "📌", [
                ("notes", None, "statements", ""),
            ]),
        ]

        results_container = st.container(height=620)
        with results_container:
            for group_title, emoji, fields in UI_GROUPS:
                # Check if ANY field in the group exists in schema
                group_fields_in_schema = [f[0] for f in fields if f[0] in schema_fields]
                if not group_fields_in_schema:
                    continue  # Skip entire group if no fields exist

                with st.expander(f"{emoji} {group_title}", expanded=exp_state):
                    has_content = False
                    for field_name, label, field_type, unit in fields:
                        if field_name not in schema_fields:
                            continue

                        if field_type == "statements":
                            if render_statements(field_name, field_name):
                                has_content = True
                            elif label:
                                st.caption(f"{label}: -")
                        elif field_type == "scalar":
                            render_scalar(label, field_name, doc.get(field_name), unit)
                            if doc.get(field_name) is not None:
                                has_content = True
                        elif field_type == "bool":
                            render_bool(label, field_name)
                            if doc.get(field_name) is not None:
                                has_content = True
                        elif field_type == "allergies":
                            allergies = doc.get("allergies") or []
                            if allergies:
                                has_content = True
                                type_labels = {"vaistai": "Vaistams", "maistas": "Maistui", "kita": "Kita"}
                                for i, a in enumerate(allergies):
                                    desc = a.get("description", "")
                                    t = type_labels.get(a.get("type", ""), a.get("type", ""))
                                    render_statement_card(f"{t}: {desc}", get_segments("allergies", desc), f"allergy_{i}")
                        elif field_type == "vaccinations":
                            vaccinations = doc.get("vaccinations") or []
                            if vaccinations:
                                has_content = True
                                for i, v in enumerate(vaccinations):
                                    name = v.get("name", "")
                                    date = v.get("date", "")
                                    lbl = f"{name} ({date})" if date else name
                                    render_statement_card(lbl, get_segments("vaccinations", name), f"vacc_{i}")

                    if not has_content:
                        st.caption("-")

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
