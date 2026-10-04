import streamlit as st
from groq import Groq
import urllib.parse

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

st.title("SI Worldwide 🌍")
st.caption("V5.1 - HD Images")

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
        t = client.audio.transcriptions.create(
            file=(audio.name, audio.getvalue()),
            model="whisper-large-v3",
            response_format="text"
        )
        voice_text = str(t)
        st.success(voice_text)
    except Exception as e:
        st.error(str(e))

text = st.text_input("Type here", placeholder="Ex: Picture of a vulture")
btn = st.button("Send ➤", use_container_width=True)

final = None
if voice_text:
    final = voice_text
elif btn and text and text!= st.session_state.last_prompt:
    final = text

if final:
    st.session_state.last_prompt = final
    fix = final.replace(" in G", " in Ga").replace("Gaun","Ga")

    # AUTO FIX spelling for images
    fix_low = fix.lower()
    fix_low = fix_low.replace("volture","vulture").replace("volture","vulture")

    st.session_state.messages.append({"role":"user","content":fix})

    is_mean = "what is" in fix_low or "meaning" in fix_low
    is_pic = ("draw" in fix_low or "picture" in fix_low or "photo" in fix_low or "image" in fix_low) and not is_mean

    if is_pic:
        clean = fix_low.replace("i want a picture of","").replace("picture of a","").replace("picture of","").replace("picture","").replace("draw","").replace("a","").strip()
        if clean == "": clean = fix
        # Better spelling
        clean = clean.replace("volture","vulture")
        # HD FLUX model - much better quality!
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(clean + " highly detailed, 8k, photorealistic") + "?model=flux&width=1024&height=1024&nologo=true&seed=42"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        system = "You are SI. Answer short, clear, friendly. If Ga language, Ga=Twi Ghana."
        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":system},{"role":"user","content":fix}],
            max_tokens=500
        )
        ans = r.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
