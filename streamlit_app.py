import streamlit as st
from groq import Groq
import urllib.parse, re, hashlib, time

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_hash" not in st.session_state:
    st.session_state.last_hash = ""

st.title("SI Worldwide 🌍")
st.caption("V5.5 - Images Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            try:
                st.image(m["content"], use_container_width=True)
            except:
                st.markdown(f"![image]({m['content']})")
        else:
            st.markdown(m["content"])

st.divider()

audio = st.audio_input("🎤 Voice")
voice_text = None
audio_hash = None
if audio:
    audio_hash = hashlib.md5(audio.getvalue()).hexdigest()
    if audio_hash!= st.session_state.last_hash:
        try:
            t = client.audio.transcriptions.create(file=(audio.name, audio.getvalue()), model="whisper-large-v3", response_format="text")
            voice_text = str(t)
            st.success(voice_text)
        except Exception as e:
            st.error(str(e))

text = st.text_input("Type here", key="input_txt", placeholder="Ex: Picture of a photographer")
btn = st.button("Send ➤", use_container_width=True)

final = None
final_hash = None

if voice_text and audio_hash:
    final = voice_text
    final_hash = audio_hash
elif btn and text.strip():
    final = text.strip()
    # Use time to allow same text again after 2 seconds
    final_hash = hashlib.md5((final + str(int(time.time()/3))).encode()).hexdigest()

if final and final_hash and final_hash!= st.session_state.last_hash:
    # Only block immediate duplicate on same rerun
    if audio_hash and audio_hash == st.session_state.last_hash:
        st.stop()
    st.session_state.last_hash = final_hash if audio_hash else hashlib.md5(final.encode()).hexdigest()

    st.session_state.messages.append({"role":"user","content":final})
    low = final.lower()

    is_image = False
    # SMART: Only image if starts with picture/draw
    if low.startswith("picture") or low.startswith("draw") or low.startswith("image") or "picture of" in low or "generate image" in low:
        is_image = True
    # But NOT for definitions
    if low.startswith("who is") or low.startswith("what is"):
        is_image = False

    if is_image:
        clean = re.sub(r'picture of a|picture of|draw a|draw|image of|a picture of', '', low).strip()
        clean = clean.replace("volture","vulture")
        if not clean:
            clean = "african photographer"
        # Better prompt + no cache + stable model
        prompt = f"{clean}, professional photo, highly detailed"
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=turbo&seed={int(time.time())}"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        system = "You are SI Worldwide, helpful Ghana AI. Short, clear."
        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":system},{"role":"user","content":final}],
            max_tokens=500
        )
        ans = r.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
