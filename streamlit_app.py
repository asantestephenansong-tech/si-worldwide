import streamlit as st
from groq import Groq
import urllib.parse, re, hashlib

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed" not in st.session_state:
    st.session_state.processed = set()

st.title("SI Worldwide 🌍")
st.caption("V5.3 - No Repeat")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

audio = st.audio_input("🎤 Voice")
voice_text = None
audio_hash = None
if audio:
    audio_hash = hashlib.md5(audio.getvalue()).hexdigest()
    # Only transcribe if never processed before
    if audio_hash not in st.session_state.processed:
        try:
            t = client.audio.transcriptions.create(file=(audio.name, audio.getvalue()), model="whisper-large-v3", response_format="text")
            voice_text = str(t)
            st.success(f"You said: {voice_text}")
        except Exception as e:
            st.error(str(e))

text = st.text_input("Type here", key="txt", placeholder="Ex: How do you say come in French?")
btn = st.button("Send ➤", use_container_width=True)

final = None
final_hash = None
if voice_text and audio_hash:
    final = voice_text
    final_hash = audio_hash
elif btn and text.strip():
    final = text.strip()
    final_hash = hashlib.md5(final.encode()).hexdigest() + "_text"
    # Clear the input box after send
    st.session_state.txt = ""

# STOP REPEAT LOGIC
if final and final_hash and final_hash not in st.session_state.processed:
    st.session_state.processed.add(final_hash)

    fix = final.replace(" in G", " in Ga").replace("Gaun","Ga")
    st.session_state.messages.append({"role":"user","content":fix})
    low = fix.lower()

    is_image = False
    if re.search(r'\b(picture of|draw|generate image|create image)\b', low) or low.startswith("picture") or low.startswith("draw"):
        is_image = True
    if "who is" in low or "what is" in low or "how do you say" in low:
        is_image = False

    if is_image:
        clean = re.sub(r'picture of a|picture of|draw a|draw|image of', '', low).strip().replace("volture","vulture")
        if not clean: clean = "vulture"
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(clean) + "?width=1024&height=1024&nologo=true&model=turbo"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        system = "You are SI Worldwide Ghana AI. Answer short, friendly, accurate. Ga: Come=Ba, Twi: Come=Bra, French: Come=venir"
        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":system},{"role":"user","content":fix}],
            max_tokens=500
        )
        ans = r.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
