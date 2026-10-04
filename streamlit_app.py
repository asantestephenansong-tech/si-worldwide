import streamlit as st
from groq import Groq
import urllib.parse, re
import streamlit.components.v1 as components

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_voice_id" not in st.session_state:
    st.session_state.last_voice_id = None

def clean_text(t):
    t = re.sub(r'\*\*|__|\*|#|•|`', ' ', t)
    t = re.sub(r'https?://\S+', ' ', t)
    return t[:400].replace("'", "").replace('"', '').replace("\n", " ")

ALL_LANGS = [
    "Auto-detect (ANY language)",
    "English", "Twi (Akan)", "Ga", "Ewe", "Hausa", "Fante",
    "French", "Spanish", "Portuguese", "German", "Italian", "Dutch", "Russian",
    "Arabic", "Hindi", "Chinese", "Japanese", "Korean", "Thai", "Vietnamese", "Indonesian",
    "Turkish", "Swahili", "Yoruba", "Igbo", "Zulu", "Amharic", "Somali", "Pidgin"
]

LANG_VOICE = {
    "English": "en-US",
    "Twi (Akan)": "en-GH",
    "Ga": "en-GH",
    "Ewe": "en-GH",
    "Hausa": "en-NG",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "Portuguese": "pt-PT",
    "German": "de-DE",
    "Russian": "ru-RU",
    "Arabic": "ar-SA",
    "Hindi": "hi-IN",
    "Chinese": "zh-CN",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Swahili": "sw-KE",
    "Yoruba": "yo-NG"
}

with st.sidebar:
    st.title("🌍 SI Controls")
    lang = st.selectbox("Answer Language", ALL_LANGS, index=0, key="lang_v45")
    speak = st.checkbox("🔊 Speak Answer", value=True, key="speak_v45")
    st.divider()
    if st.button("🗑️ Clear Chat", key="clear_v45"):
        st.session_state.messages = []
        st.session_state.last_voice_id = None
        st.rerun()

st.title("SI Worldwide 🌍")
st.caption("V4.5 - All Languages + Image Fix")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st
