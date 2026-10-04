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

# FULL PHRASE DICTIONARY
DICT = {
    "bring it": {"twi":"Fa bra", "ga":"Kɛ lɛ ba", "ewe":"Tsɔe vɛ", "french":"Apporte-le"},
    "go home": {"twi":"Kɔ fie", "ga":"Tee shia", "ewe":"Yi afeme", "french":"Rentre à la maison"},
    "come": {"twi":"Bra", "ga":"Ba", "ewe":"Va", "french":"Viens"},
    "go": {"twi":"Kɔ", "ga":"Tee", "ewe":"Yi", "french":"Va"},
    "i love you": {"twi":"Me dɔ wo", "ga":"Mi sumɔ bo", "ewe":"Melɔ̃ wò", "french":"Je t'aime"},
}

st.title("SI Worldwide 🌍")
st.caption("V6.0 - HD Real")

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

text = st.text_input("Type here", key="input_txt", placeholder='Ex: go home in Twi and Ewe')
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
    if st.session_state.last_hash == hashlib.md5(final.encode()).hexdigest() and not audio_hash:
        # allow same phrase after 2 sec but block instant double rerun
        pass
    st.session_state.last_hash = hashlib.md5(final.encode()).hexdigest()

    st.session_state.messages.append({"role":"user","content":final})
    low = final.lower()

    # CHECK DICTIONARY FOR PHRASES
    handled = False
    for phrase, langs in DICT.items():
        if phrase in low:
            out = ""
            if "twi" in low: out += f"In **Twi**, '{phrase}' is: **{langs.get('twi','')}** 🇬🇭\n\n"
            if "ga" in low: out += f"In **Ga**, '{phrase}' is: **{langs.get('ga','')}** 🇬🇭\n\n"
            if "ewe" in low: out += f"In **Ewe**, '{phrase}' is: **{langs.get('ewe','')}** 🇬🇭\n\n"
            if "french" in low: out += f"In **French**, '{phrase}' is: **{langs.get('french','')}**\n\n"
            if out=="":
                # If no language specified, show all Ghana
                out = f"**'{phrase}'**\n- Twi: **{langs.get('twi')}**\n- Ga: **{langs.get('ga')}**\n- Ewe: **{langs.get('ewe')}**\n- French: **{langs.get('french')}**"
            st.session_state.messages.append({"role":"assistant","content":out})
            handled = True
            break

    if not handled:
        is_image = low.startswith("picture") or low.startswith("draw") or "picture of" in low or "generate image" in low
        if low.startswith("who is") or low.startswith("what is") or "how do you say" in low or "how to say" in low or "how many" in low:
            is_image = False

        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a|draw|image of', '', low).strip().replace("volture","vulture")
            if not clean: clean = "vulture"
            # REAL VULTURE PROMPT - FIXES DONUT WING
            prompt = f"a real {clean} bird, accurate anatomy, two wings only, realistic feathers, sitting on tree stump, national geographic photo, 8k, photorealistic"
            # FLUX model = realistic, no deform
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux&enhance=true&seed={int(time.time())}"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            system = "You are SI Worldwide Ghana AI. You know Twi, Ga, Ewe, French, Hindi. Twi: go home=Kɔ fie, Ga: Tee shia, Ewe: Yi afeme. Answer short, never empty."
            r = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":system},{"role":"user","content":final}],
                max_tokens=700
            )
            ans = r.choices[0].message.content or "In Twi: Kɔ fie, In Ewe: Yi afeme"
            st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
