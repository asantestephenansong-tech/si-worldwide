import streamlit as st
from groq import Groq
import urllib.parse, re

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SI Worldwide 🌍")
st.caption("V4.8 - Phone Safe")

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

text = st.text_input("Type here", placeholder="Example: picture of a motorbike")
btn = st.button("Send ➤")

final = None
if voice_text:
    final = voice_text
elif btn and text:
    final = text

if final:
    st.session_state.messages.append({"role":"user","content":final})

    low = final.lower()
    is_mean = "what is" in low or "meaning" in low
    is_pic = ("draw" in low or "picture" in low or "photo" in low) and not is_mean

    if is_pic:
        clean = low.replace("i want a picture of","").replace("picture of","").replace("draw","").strip()
        if clean == "":
            clean = final
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(clean) + "?width=1024&height=1024&nologo=true"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        try:
            chat = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":"You are SI. Answer short plain text."},{"role":"user","content":final}],
                max_tokens=500
            )
            ans = chat.choices[0].message.content
            st.session_state.messages.append({"role":"assistant","content":ans})
        except Exception as e:
            st.session_state.messages.append({"role":"assistant","content":f"Error: {e}"})

    st.rerun()
