
import streamlit as st
import requests
import time
from datetime import datetime

# ============================================================
# BASEAI FRONTEND
# Streamlit frontend for the Voice AI Number System Converter
# ============================================================

st.set_page_config(
    page_title="Okay Bot - Voice Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------- CONFIG ----------------------

BACKEND_URL = st.sidebar.text_input(
    "Backend API URL",
    value="http://127.0.0.1:8000",
    help="Ask your backend teammate for the URL/port.",
).rstrip("/")

if "history" not in st.session_state:
    st.session_state.history = []

if "command" not in st.session_state:
    st.session_state.command = ""

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------------------- CSS ----------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

:root {
    --green: #79ff35;
    --green2: #45d51d;
    --dark: #020502;
    --panel: #050a05;
    --line: #254b1b;
    --muted: #9ba596;
}

html, body, [class*="css"] {
    font-family: "Share Tech Mono", monospace !important;
}

.stApp {
    background:
        radial-gradient(circle at 70% 20%, rgba(65,255,30,.035), transparent 35%),
        #020402;
    color: #e9f5e7;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding: 0.6rem 0.8rem 0.5rem 0.8rem !important;
    max-width: 100% !important;
}

[data-testid="stSidebar"] {
    background: #020402;
    border-right: 1px solid var(--line);
    min-width: 300px;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.1rem 1.1rem;
}

.logo {
    color: var(--green);
    font-size: 34px;
    line-height: 1;
    margin: 5px 0 10px;
}

.brand {
    color: var(--green);
    font-size: 27px;
    font-weight: 700;
    letter-spacing: 1px;
}

.tagline {
    color: var(--green);
    font-size: 13px;
    margin-top: 10px;
}

.topbar {
    border: 1px solid var(--line);
    height: 60px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--green);
    background: #030703;
}

.listen {
    color: var(--green);
    white-space: nowrap;
}

.dot {
    display:inline-block;
    width:10px;
    height:10px;
    border-radius:50%;
    background:var(--green);
    box-shadow:0 0 12px var(--green);
    margin-right:8px;
}

.hero {
    text-align:center;
    padding: 25px 10px 18px;
    border-bottom: 1px solid #172c12;
}

.mic {
    font-size: 82px;
    color: var(--green);
    text-shadow: 0 0 22px rgba(121,255,53,.35);
    line-height: 1;
}

.wave {
    color: var(--green);
    letter-spacing: 6px;
    font-size: 23px;
    margin: 8px 0 18px;
}

.hero-title {
    color: var(--green);
    font-size: 17px;
}

.section-title {
    color: var(--green);
    font-size: 16px;
    margin: 18px 0 10px;
}

.panel {
    border: 1px solid #28551e;
    border-radius: 9px;
    background: rgba(2,8,2,.72);
    padding: 18px;
}

.example {
    border: 1px solid #28551e;
    border-radius: 8px;
    padding: 13px 18px;
    color: var(--green);
    line-height: 1.8;
    background: #020602;
}

.console {
    border: 1px solid #28551e;
    border-radius: 9px;
    background: #020502;
    padding: 18px 20px;
    min-height: 360px;
}

.console-line {
    line-height: 1.8;
    margin: 2px 0;
}

.green {
    color: var(--green);
}

.white {
    color: #e6e9e5;
}

.muted {
    color: var(--muted);
}

.result {
    border: 2px dashed var(--green);
    border-radius: 9px;
    display: inline-block;
    padding: 12px 32px;
    color: var(--green);
    font-size: 22px;
    margin: 10px 0;
    text-align:center;
}

.reference {
    border: 1px solid #28551e;
    border-radius: 8px;
    padding: 16px;
    height: 100%;
}

.status-card {
    border: 1px solid #28551e;
    border-radius: 8px;
    padding: 16px;
    color: var(--green);
    margin-top: 230px;
}

.footer {
    border-top: 1px solid #1a3514;
    padding: 10px 18px;
    color: #55c936;
    font-size: 13px;
    display:flex;
    justify-content:space-between;
}

div.stButton > button {
    background: #050b05 !important;
    border: 1px solid #3c8b28 !important;
    color: var(--green) !important;
    border-radius: 7px !important;
    font-family: "Share Tech Mono", monospace !important;
}

div.stButton > button:hover {
    border-color: var(--green) !important;
    box-shadow: 0 0 12px rgba(121,255,53,.18);
}

.stTextInput input, .stTextArea textarea {
    background:#030603 !important;
    color:#e9f5e7 !important;
    border:1px solid #28551e !important;
    font-family:"Share Tech Mono", monospace !important;
}

[data-testid="stFileUploader"] {
    border: 1px solid #28551e;
    border-radius: 8px;
    background:#030603;
}

.small-note {
    color:#6e7d6a;
    font-size:12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- HELPERS ----------------------

def call_convert(number, from_base, to_base):
    payload = {
        "number": number,
        "from_base": from_base,
        "to_base": to_base,
    }
    response = requests.post(
        f"{BACKEND_URL}/api/convert",
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()

def call_voice(audio_file):
    files = {
        "audio": (
            audio_file.name,
            audio_file.getvalue(),
            audio_file.type or "audio/wav",
        )
    }
    response = requests.post(
        f"{BACKEND_URL}/api/voice",
        files=files,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

def show_conversion(data):
    number = str(data.get("number", ""))
    source = data.get("source_base", data.get("from_base", "?"))
    target = data.get("target_base", data.get("to_base", "?"))
    result = str(data.get("result", ""))
    steps = data.get("steps", [])

    st.markdown(
        f'<div class="console">'
        f'<div class="console-line"><span class="green">Okay Bot:</span> '
        f'<span class="white">Processing your request...</span></div>'
        f'<div class="console-line">&nbsp;&nbsp;'
        f'<span class="muted">Source Base :</span> {source}</div>'
        f'<div class="console-line">&nbsp;&nbsp;'
        f'<span class="muted">Target Base :</span> {target}</div>'
        f'<div class="console-line"><span class="green">Okay Bot:</span> '
        f'<span class="white">Converting...</span></div>'
        f'<div class="console-line"><span class="green">Okay Bot:</span> '
        f'<span class="green">Conversion Successful! ✓</span></div>'
        f'<div style="text-align:center">'
        f'<div class="result">{number}<sub>{source}</sub> &nbsp;=&nbsp; '
        f'{result}<sub>{target}</sub></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if steps:
        with st.expander("Show conversion steps"):
            if isinstance(steps, list):
                for i, step in enumerate(steps, 1):
                    st.write(f"{i}. {step}")
            else:
                st.write(steps)

# ---------------------- SIDEBAR ----------------------

with st.sidebar:
    st.markdown('<div class="logo">♙</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand">OKAY BOT</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tagline">AI NUMBER SYSTEM CONVERTER</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🎙 Voice Assistant",
            "▦ Converter",
            "◷ History",
            "</> How It Works",
            "ⓘ About",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="status-card">'
        '<b>SYSTEM STATUS</b><br><br>'
        '● LISTENING...<br><br>'
        'Say “Okay Bot”<br><br>'
        '<span style="font-size:22px">▂▅▂▇▃▆▂▅</span><br><br>'
        '▮▮▮▮▮▮▮▮▮▯▯▯'
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------------- TOP BAR ----------------------

st.markdown(
    '<div class="topbar">'
    '<span>&gt; OKAY BOT - VOICE ASSISTANT</span>'
    '<span class="listen"><span class="dot"></span>LISTENING</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------- VOICE PAGE ----------------------

if page == "🎙 Voice Assistant":

    st.markdown(
        '<div class="hero">'
        '<div class="mic">♩</div>'
        '<div class="wave">···▂▅▂▇▃▆▂▅▂···</div>'
        '<div class="hero-title">'
        'Listening... Say “Okay Bot” followed by your conversion request.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">EXAMPLE COMMANDS</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="example">'
        '1) Convert 101101 from binary to hexadecimal<br>'
        '2) Convert 255 from decimal to binary<br>'
        '3) Convert 7B from hexadecimal to decimal<br>'
        '4) Convert 725 from octal to binary'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([4, 1.1], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            '<span class="green">&gt; Waiting for your command...</span>',
            unsafe_allow_html=True,
        )

        # Streamlit's browser microphone recorder.
        audio = st.audio_input("Record your command")

        command_text = st.text_input(
            "Or type your command",
            placeholder='Okay Bot, convert 101101 from binary to hexadecimal',
            label_visibility="collapsed",
        )

        c1, c2 = st.columns([1, 1])

        with c1:
            process = st.button("▶ PROCESS COMMAND", use_container_width=True)

        with c2:
            if st.button("CLEAR", use_container_width=True):
                st.session_state.command = ""
                st.session_state.last_result = None
                st.rerun()

        if process:
            # 1. Agar text box mein likha hai, toh TYPED text ko sabse pehle chalao
            if command_text.strip():
                st.session_state.command = command_text.strip()
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/command",
                        json={"command": command_text.strip()},
                        timeout=30,
                    )
                    response.raise_for_status()
                    data = response.json()

                    if data.get("conversion"):
                        st.session_state.last_result = data["conversion"]

                except requests.RequestException:
                    st.warning(
                        "Text command saved, but the backend could not be reached."
                    )

            # 2. Agar text box khali hai, tab voice audio chalao
            elif audio is not None:
                try:
                    data = call_voice(audio)
                    transcript = data.get("transcript", "")
                    st.session_state.command = transcript

                    if data.get("conversion"):
                        st.session_state.last_result = data["conversion"]

                    st.success(f"You: {transcript}")
                except requests.RequestException as e:
                    st.error(
                        "Backend is not reachable. Check the Backend API URL "
                        "and make sure your friend's server is running."
                    )
                except Exception as e:
                    st.error(f"Voice request failed: {e}")
        if st.session_state.command:
            st.markdown(
                f'<div class="console">'
                f'<div class="console-line"><span class="green">You:</span> '
                f'<span class="white">{st.session_state.command}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if st.session_state.last_result:
            show_conversion(st.session_state.last_result)

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="reference">'
            '<div class="green">BASE REFERENCE</div><br>'
            '2&nbsp;&nbsp;→&nbsp;&nbsp;Binary<br><br>'
            '8&nbsp;&nbsp;→&nbsp;&nbsp;Octal<br><br>'
            '10 →&nbsp;&nbsp;Decimal<br><br>'
            '16 →&nbsp;&nbsp;Hexadecimal<br><br>'
            '<hr>'
            '<span class="green">Digits Used:</span><br><br>'
            '0-9, A-F'
            '</div>',
            unsafe_allow_html=True,
        )

# ---------------------- CONVERTER PAGE ----------------------

elif page == "▦ Converter":

    st.markdown('<div class="section-title">MANUAL CONVERTER</div>', unsafe_allow_html=True)

    with st.form("converter_form"):
        number = st.text_input("Number", placeholder="e.g. 101101 or 7B")
        c1, c2 = st.columns(2)

        with c1:
            from_base = st.number_input("Source Base", min_value=2, max_value=36, value=2)

        with c2:
            to_base = st.number_input("Target Base", min_value=2, max_value=36, value=16)

        submitted = st.form_submit_button("✨ CONVERT", use_container_width=True)

    if submitted:
        try:
            data = call_convert(number, int(from_base), int(to_base))
            st.session_state.last_result = data
            st.session_state.history.insert(0, data)
            show_conversion(data)
        except requests.RequestException:
            st.error("Backend not reachable. Start your friend's API server.")
        except Exception as e:
            st.error(f"Conversion failed: {e}")

# ---------------------- HISTORY PAGE ----------------------

elif page == "◷ History":

    st.markdown('<div class="section-title">CONVERSION HISTORY</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown(
            '<div class="panel muted">No conversions in this session yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        for item in st.session_state.history:
            st.markdown(
                f'<div class="panel" style="margin-bottom:10px">'
                f'<span class="green">{item.get("number","")}</span>'
                f' &nbsp;→&nbsp; '
                f'<span class="green">{item.get("result","")}</span>'
                f' &nbsp;&nbsp; '
                f'base {item.get("source_base", item.get("from_base","?"))}'
                f' → '
                f'base {item.get("target_base", item.get("to_base","?"))}'
                f'</div>',
                unsafe_allow_html=True,
            )

# ---------------------- HOW IT WORKS ----------------------

elif page == "</> How It Works":

    st.markdown('<div class="section-title">HOW THE SYSTEM WORKS</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="panel">'
        '<span class="green">1. VOICE INPUT</span><br>'
        'The user speaks a natural-language conversion command.<br><br>'
        '<span class="green">2. SPEECH-TO-TEXT</span><br>'
        'The backend converts the recorded audio into text.<br><br>'
        '<span class="green">3. AI/NLP UNDERSTANDING</span><br>'
        'The backend extracts the number, source base and target base.<br><br>'
        '<span class="green">4. PYTHON CONVERSION ENGINE</span><br>'
        'The number is converted between bases 2-36.<br><br>'
        '<span class="green">5. RESULT + EXPLANATION</span><br>'
        'The frontend displays the result and conversion steps.'
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------------- ABOUT ----------------------

# ---------------------- ABOUT ----------------------

elif page == "ⓘ About":

    st.markdown('<div class="section-title">ABOUT OKAY BOT & DEVELOPMENT TEAM</div>', unsafe_allow_html=True)

    # 1. Project Overview Card
    st.markdown(
        '<div class="panel" style="margin-bottom: 15px;">'
        '<h3 class="green" style="margin-top:0;">⚡ Okay Bot - AI Number System Converter</h3>'
        'An intelligent conversational agent engineered for multi-base conversions, '
        'strict radix validation, and step-by-step mathematical reasoning.<br><br>'
        '<span class="green">📚 Course:</span> Digital Electronics &nbsp;|&nbsp; '
        '<span class="green">🎓 Program:</span> B.Tech (IMVT / CSE)<br>'
        '<span class="green">🛠️ Architecture:</span> Full-Stack (Streamlit Cyber UI + FastAPI Backend Server)'
        '</div>',
        unsafe_allow_html=True,
    )

    # 2. Team Contribution & Roles Card
    st.markdown(
        '<div class="panel">'
        '<h4 class="green" style="margin-top:0;">👥 PROJECT TEAM & RESPONSIBILITIES</h4>'
        '<hr style="border: 0; border-top: 1px solid var(--line); margin: 8px 0 15px 0;">'
        
        # Member 1 - Anurag
        '<div style="margin-bottom: 14px;">'
        '<b class="white">1. ANURAG (Frontend Lead):</b><br>'
        '<span class="green">↳ Role:</span> Streamlit UI/UX architecture, Cyberpunk terminal theme styling, and Voice recording integration.'
        '</div>'
        
        # Member 2 - Himanshu
        '<div style="margin-bottom: 14px;">'
        '<b class="white">2. HIMANSHU (Backend & Core Engine Lead):</b><br>'
        '<span class="green">↳ Role:</span> FastAPI backend API server, Positional expansion & division algorithms, Radix validation, and Error handling.'
        '</div>'
        
        # Member 3 - Divyansh
        '<div style="margin-bottom: 14px;">'
        '<b class="white">3. DIVYANSH (Documentation Lead):</b><br>'
        '<span class="green">↳ Role:</span> Comprehensive Project Report (PDF), System architecture design, Test case documentation, and References.'
        '</div>'
        
        # Member 4 - Naman
        '<div>'
        '<b class="white">4. NAMAN (Video Demonstration Lead):</b><br>'
        '<span class="green">↳ Role:</span> Complete 5-8 minute System Demo Video production, Voiceover explanation, and Feature walkthrough.'
        '</div>'
        
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------------- FOOTER ----------------------

st.markdown(
    '<div class="footer">'
    '<span>&gt; Built with ♡ using Streamlit &nbsp;|&nbsp; '
    'AI understands • Python converts • You learn</span>'
    f'<span>{datetime.now().strftime("%H:%M:%S")}</span>'
    '</div>',
    unsafe_allow_html=True,
)

