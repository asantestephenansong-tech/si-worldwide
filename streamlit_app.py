import streamlit as st
from groq import Groq
import urllib.parse, re

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

st.title("SI Worldwide 🌍")
st.caption("V5.2 - Smart Detector")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()
audio = st.audio_input("🎤 Voice")
voice_text = None
if audio:
    try:
        t = client.audio.transcriptions.create(file=(audio.name, audio.getvalue()), model="whisper-large-v3", response_format="text")
        voice_text = str(t)
        st.success(voice_text)
    except Exception as e:
        st.error(str(e))

text = st.text_input("Type here", placeholder="Ex: Picture of a vulture or Who is a photographer?")
btn = st.button("Send ➤", use_container_width=True)

final = None
if voice_text:
    final = voice_text
elif btn and text and text!= st.session_state.last_prompt:
    final = text

if final:
    st.session_state.last_prompt = final
    st.session_state.messages.append({"role":"user","content":final})
    low = final.lower()

    # SMART IMAGE DETECTOR - FIX photographer bug
    # Only trigger if starts with picture/draw OR has "picture of" etc, NOT if word contains photo
    is_image = False
    if re.search(r'\b(picture of|draw|generate image|create image|make an image)\b', low):
        is_image = True
    # Also allow "picture of a vulture" but NOT "photographer"
    if low.startswith("picture") or low.startswith("draw") or low.startswith("image of"):
        is_image = True

    # Don't trigger for who is a photographer / philosopher / etc
    if "who is" in low or "what is" in low or "meaning" in low:
        is_image = False

    if is_image:
        clean = re.sub(r'picture of a|picture of|draw a|draw|image of', '', low).strip()
        clean = clean.replace("volture","vulture")
        if clean == "": clean = "vulture"
        # Use turbo model - fastest and stable, no flux overload
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(clean) + "?width=1024&height=1024&nologo=true&model=turbo"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        system = "You are SI Worldwide. Answer short and clear. If Ga language: Come=Ba."
        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":system},{"role":"user","content":final}],
            max_tokens=500
        )
        ans = r.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
