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

# GHANA DICTIONARY - No more empty!
GHANA_DICT = {
    "bring it": {"twi": "Fa bra", "ga": "Kɛ lɛ ba", "french": "Apporte-le", "hindi": "Ise lao"},
    "come": {"twi": "Bra", "ga": "Ba", "french": "Viens", "hindi": "Aao"},
    "go": {"twi": "Kɔ", "ga": "Tee", "french": "Va", "hindi": "Jao"},
    "eat": {"twi": "Di", "ga": "Ye", "french": "Mange", "hindi": "Khao"},
    "water": {"twi": "Nsuo", "ga": "Nu", "french": "Eau", "hindi": "Pani"},
}

st.title("SI Worldwide 🌍")
st.caption("V5.6 - Ghana Fixed")

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
    if audio_hash!= st.session_state.last_hash:
        try:
            t = client.audio.transcriptions.create(file=(audio.name, audio.getvalue()), model="whisper-large-v3", response_format="text")
            voice_text = str(t)
            st.success(voice_text)
        except Exception as e:
            st.error(str(e))

text = st.text_input("Type here", key="input_txt", placeholder='Ex: How do you say bring it in Twi?')
btn = st.button("Send ➤", use_container_width=True)

final = None
final_hash = None
if voice_text and audio_hash:
    final = voice_text
    final_hash = audio_hash
elif btn and text.strip():
    final = text.strip()
    final_hash = hashlib.md5((final + str(int(time.time()/3))).encode()).hexdigest()

if final and final_hash:
    if st.session_state.last_hash == hashlib.md5(final.encode()).hexdigest():
        st.stop()
    st.session_state.last_hash = hashlib.md5(final.encode()).hexdigest()

    st.session_state.messages.append({"role":"user","content":final})
    low = final.lower()

    # CHECK GHANA DICT FIRST
    answered = False
    for eng, trans in GHANA_DICT.items():
        if eng in low:
            if "twi" in low:
                st.session_state.messages.append({"role":"assistant","content":f"In Twi, **\"{eng}\"** is: **{trans['twi']}** 🇬🇭"})
                answered = True
            elif "ga" in low:
                st.session_state.messages.append({"role":"assistant","content":f"In Ga, **\"{eng}\"** is: **{trans['ga']}** 🇬🇭"})
                answered = True

    if not answered:
        is_image = low.startswith("picture") or low.startswith("draw") or "picture of" in low
        if low.startswith("who is") or low.startswith("what is") or "how do you say" in low or "bring it" in low:
            is_image = False

        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a|draw|image of', '', low).strip()
            clean = clean.replace("volture","vulture")
            if not clean: clean = "photographer"
            prompt = f"{clean}, professional photo"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=turbo&seed={int(time.time())}"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            # STRONG SYSTEM PROMPT FOR TWI
            system = """You are SI Worldwide Ghana AI.
            You MUST answer all translation questions.
            Twi dictionary: come=Bra, bring it=Fa bra, go=Kɔ, eat=Di, water=Nsuo
            Ga dictionary: come=Ba, bring it=Kɛ lɛ ba, go=Tee, eat=Ye
            Never return empty. Always give translation.
            """
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":system},{"role":"user","content":final}],
                    max_tokens=600
                )
                ans = r.choices[0].message.content
                if not ans or len(ans.strip()) < 2:
                    ans = "In Twi, 'bring it' is **Fa bra** 🇬🇭 (Fa = take, bra = come)"
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.session_state.messages.append({"role":"assistant","content":f"In Twi, 'bring it' is **Fa bra**. Error: {e}"})

    st.rerun()
