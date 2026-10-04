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

ALL_LANGS = ["Auto-detect (ANY language)","English","Twi (Akan)","Ga","Ewe","Hausa","Fante","French","Spanish","Portuguese","German","Italian","Dutch","Russian","Arabic","Hindi","Chinese","Japanese","Korean","Thai","Vietnamese","Indonesian","Turkish","Swahili","Yoruba","Igbo","Zulu","Pidgin"]
LANG_VOICE = {"English":"en-US","Twi (Akan)":"en-GH","Ga":"en-GH","Ewe":"en-GH","Hausa":"en-NG","French":"fr-FR","Spanish":"es-ES","German":"de-DE","Russian":"ru-RU","Arabic":"ar-SA","Hindi":"hi-IN","Chinese":"zh-CN","Japanese":"ja-JP"}

with st.sidebar:
    st.title("🌍 SI Controls")
    lang = st.selectbox("Answer Language", ALL_LANGS, index=0)
    speak = st.checkbox("🔊 Speak Answer", value=True)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_voice_id = None
        st.rerun()

st.title("SI Worldwide 🌍")
st.caption("V4.7 - Big Images Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

st.write("🎤 Voice")
audio = st.audio_input("Tap to record", key="audio_v47")
voice_prompt = None
if audio:
    audio_id = getattr(audio, 'file_id', str(len(audio.getvalue())))
    if audio_id != st.session_state.last_voice_id:
        with st.spinner("Listening..."):
            try:
                tr = client.audio.transcriptions.create(
                    file=(audio.name, audio.getvalue()),
                    model="whisper-large-v3",
                    prompt="Twi Ga Ewe Hausa English French Arabic Hindi Chinese Spanish",
                    response_format="text"
                )
                voice_prompt = tr
                st.session_state.last_voice_id = audio_id
                st.success(f"You said: {tr}")
            except Exception as e:
                st.error(f"{e}")

st.write("💬 Type")
col1, col2 = st.columns([4,1])
with col1:
    text_prompt = st.text_input("Type in ANY language", placeholder="Example: picture of a motorbike", key="text_v47", label_visibility="collapsed")
with col2:
    send_btn = st.button("Send ➤", use_container_width=True, key="send_v47")

final_prompt = None
if voice_prompt:
    final_prompt = voice_prompt
elif send_btn and text_prompt:
    final_prompt = text_prompt

if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)
    with st.chat_message("assistant"):
        low = final_prompt.lower()
        is_meaning_question = "what is" in low or "meaning" in low or "translate" in low or "means" in low
        is_image_request = ("draw" in low or "picture" in low or "photo" in low or "image" in low)
        is_image = is_image_request and not is_meaning_question
        if lang.startswith("Auto"):
            lang_inst = "Detect language and answer in SAME language."
        else:
            lang_inst = f"Respond ONLY in {lang}."
        if is_image:
            clean_prompt = low.replace("i want a picture of","").replace("i want","").replace("picture of","").replace("a picture","").replace("draw","").strip()
            if not clean_prompt:
                clean_prompt = final_prompt
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=1024&height=1024&seed=7&nologo=true"
            st.image(url, use_container_width=True)
            st.caption(f"🎨 {clean_prompt}")
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": url})
        else:
            try:
                r = client.chat.completions.create(
