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

# V6.2 DICT - SORTED LONGEST FIRST
DICT = {
    "go and sleep": {"twi":"Kɔ bɛda", "ga":"Tee ya wɔ", "ewe":"Yi dɔ alɔ", "hindi":"Jao aur so jao", "german":"Geh und schlaf", "french":"Va dormir"},
    "go to sleep": {"twi":"Kɔ bɛda", "ga":"Tee ya wɔ", "ewe":"Yi dɔ alɔ", "hindi":"Sone jao", "german":"Geh schlafen", "french":"Va dormir"},
    "go home": {"twi":"Kɔ fie", "ga":"Tee shia", "ewe":"Yi afeme", "hindi":"Ghar jao", "german":"Geh nach Hause", "french":"Rentre à la maison"},
    "bring it": {"twi":"Fa bra", "ga":"Kɛ lɛ ba", "ewe":"Tsɔe vɛ", "hindi":"Ise lao", "german":"Bring es", "french":"Apporte-le"},
    "i love you": {"twi":"Me dɔ wo", "ga":"Mi sumɔ bo", "ewe":"Melɔ̃ wò", "hindi":"Main tumse pyar karta hoon", "german":"Ich liebe dich", "french":"Je t'aime"},
    "come": {"twi":"Bra", "ga":"Ba", "ewe":"Va", "hindi":"Aao", "german":"Komm", "french":"Viens"},
    "go": {"twi":"Kɔ", "ga":"Tee", "ewe":"Yi", "hindi":"Jao", "german":"Geh", "french":"Va"},
    "sleep": {"twi":"Da", "ga":"Wɔ", "ewe":"Dɔ alɔ", "hindi":"So jao", "german":"Schlaf", "french":"Dors"},
}

st.title("SI Worldwide 🌍")
st.caption("V6.2 - Phrase Fix")

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

text = st.text_input("Type here", key="input_txt", placeholder='go and sleep in hindi and german')
btn = st.button("Send ➤", use_container_width=True)

final = None
final_hash = None
if voice_text and audio_hash:
    final = voice_text
    final_hash = audio_hash
elif btn and text.strip():
    final = text.strip()
    final_hash = hashlib.md5((final + str(time.time())).encode()).hexdigest()

if final and final_hash:
    st.session_state.last_hash = hashlib.md5(final.encode()).hexdigest()
    st.session_state.messages.append({"role":"user","content":final})
    low = final.lower().replace('"',' ').replace("'"," ").strip()

    # EXTRACT PHRASE - Look for what is inside quotes or longest match
    # Try to find phrase to translate
    target_phrase = None
    # Sort keys by length longest first!
    for phrase in sorted(DICT.keys(), key=len, reverse=True):
        if phrase in low:
            target_phrase = phrase
            break

    handled = False
    if target_phrase:
        langs = DICT[target_phrase]
        out = f"**'{target_phrase}'** means:\n\n"
        has_lang = False
        if "twi" in low:
            out += f"- **Twi**: **{langs.get('twi')}** 🇬🇭\n"
            has_lang = True
        if "ga" in low and "germany" not in low.split("ga")[0][-10:]: # avoid ga in germany confusion
            # better check
            if re.search(r'\bga\b', low):
                out += f"- **Ga**: **{langs.get('ga')}** 🇬🇭\n"
                has_lang = True
        if "ewe" in low:
            out += f"- **Ewe**: **{langs.get('ewe')}** 🇬🇭\n"
            has_lang = True
        if "hindi" in low:
            out += f"- **Hindi**: **{langs.get('hindi')}** 🇮🇳\n"
            has_lang = True
        if "german" in low or "germany" in low:
            out += f"- **German**: **{langs.get('german')}** 🇩🇪\n"
            has_lang = True
        if "french" in low:
            out += f"- **French**: **{langs.get('french')}** 🇫🇷\n"
            has_lang = True

        if not has_lang:
            # show all
            for k,v in langs.items():
                out += f"- {k.title()}: **{v}**\n"

        st.session_state.messages.append({"role":"assistant","content":out})
        handled = True

    if not handled:
        is_image = low.startswith("picture") or low.startswith("draw") or "picture of" in low
        if any(x in low for x in ["who is","what is","how do you say","how to say","how many","translate"]):
            is_image = False
        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a|draw|image of', '', low).strip().replace("volture","vulture")
            if not clean: clean = "vulture"
            prompt = f"a real {clean}, accurate anatomy, photorealistic, national geographic, 8k"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux&enhance=true&seed={int(time.time())}"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            system = "You are SI Worldwide, expert translator Twi, Ga, Ewe, Hindi, German, French. If user says Germany, means German language. Never answer only 'go' when user says 'go and sleep'. Always translate full phrase."
            try:
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":system},{"role":"user","content":final}],
                    max_tokens=800
                )
                ans = r.choices[0].message.content
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.session_state.messages.append({"role":"assistant","content":f"Error: {e}"})

    st.rerun()
