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

st.title("SI Worldwide 🌍")
st.caption("V5.0 - Voice Fix")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

st.write("🎤 Voice")
audio = st.audio_input("Tap to record")
voice_text = None

# Backup uploader if mic fails
up = st.file_uploader("Or upload voice if mic error", type=["mp3","wav","m4a","ogg"])

audio_file = audio or up

if audio_file:
    try:
        t = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.getvalue()),
            model="whisper-large-v3",
            response_format="text"
        )
        voice_text = str(t)
        st.success(f"You said: {voice_text}")
    except Exception as e:
        st.error(f"Voice error: {e}")

text = st.text_input("Type here", placeholder="Ex: How do you say come in Ga?")
btn = st.button("Send ➤", use_container_width=True)

final = None
if voice_text:
    final = voice_text
elif btn and text:
    final = text

if final:
    fix = final.replace(" in G", " in Ga").replace(" in g", " in Ga").replace("Gaun","Ga")
    st.session_state.messages.append({"role":"user","content":fix})

    low = fix.lower()
    is_mean = "what is" in low or "meaning" in low
    is_pic = ("draw" in low or "picture" in low or "photo" in low or "image" in low) and not is_mean

    if is_pic:
        clean = low.replace("i want a picture of","").replace("picture of","").replace("draw","").strip()
        if clean == "": clean = fix
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(clean) + "?width=1024&height=1024&nologo=true"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        system = """You are SI Worldwide, Ghana AI.
If user asks "G" means Ga language.
Ga: Come=Ba, Come in=Ba mli, How are you=Atɛ o nɛ, Thank you=Oyiwala donu
Twi: Come=Bra, Come in=Bra mu, How are you=Wo ho te sen
Keep short."""

        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":system},{"role":"user","content":fix}],
            max_tokens=400
        )
        ans = r.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
