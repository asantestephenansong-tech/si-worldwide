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

st.title("SI Worldwide 🌍")
st.caption("V7.2 - Never Empty")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

# FULL GHANA DICT - NO EMPTY EVER
DICT = {
    "i am hungry": {"twi":"Ɛkɔm de me", "ga":"Gɔmɔ mi", "hausa":"Ina jin yunwa", "ewe":"Dɔ le vuum", "hindi":"Mujhe bhookh lagi hai", "german":"Ich habe Hunger"},
    "i am thirsty": {"twi":"Nsukɔm de me", "ga":"Namɔ mi", "hausa":"Ina jin kishirwa", "german":"Ich habe Durst"},
    "let's go home": {"twi":"Momma yɛnkɔ fie", "ga":"Tee wɔ shia", "hausa":"Mu je gida", "german":"Lass uns nach Hause gehen"},
    "go and sleep": {"twi":"Kɔ bɛda", "ga":"Tee ya wɔ", "hausa":"Je ka yi bacci", "german":"Geh und schlaf", "hindi":"Jao aur so jao"},
    "go home": {"twi":"Kɔ fie", "ga":"Tee shia", "hausa":"Je gida", "german":"Geh nach Hause", "hindi":"Ghar jao"},
    "bring it": {"twi":"Fa bra", "ga":"Kɛ lɛ ba", "hausa":"Kawo shi", "german":"Bring es"},
    "i love you": {"twi":"Me dɔ wo", "ga":"Mi sumɔ bo", "hausa":"Ina sonki/so", "german":"Ich liebe dich"},
    "good morning": {"twi":"Maakye", "ga":"Atu", "hausa":"Barka da safiya", "german":"Guten Morgen"},
    "thank you": {"twi":"Medaase", "ga":"Oyiwala dɔŋŋ", "hausa":"Na gode", "german":"Danke"},
}

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Type here", placeholder="Ex: I am hungry in Twi and Hausa")
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and text.strip():
    q = text.strip()
    low = q.lower()

    last = [m for m in st.session_state.messages if m["role"]=="user"]
    if last and last[-1]["content"] == q:
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})

    handled=False
    for phrase in sorted(DICT.keys(), key=len, reverse=True):
        if phrase in low:
            langs = DICT[phrase]
            out = f"**'{phrase}'** means:\n\n"
            count=0
            if "twi" in low: out+=f"- **Twi**: **{langs.get('twi','')}** 🇬🇭\n"; count+=1
            if re.search(r'\bga\b', low): out+=f"- **Ga**: **{langs.get('ga','')}** 🇬🇭\n"; count+=1
            if "hausa" in low: out+=f"- **Hausa**: **{langs.get('hausa','')}** 🇳🇬\n"; count+=1
            if "ewe" in low: out+=f"- **Ewe**: **{langs.get('ewe','')}** 🇬🇭\n"; count+=1
            if "hindi" in low: out+=f"- **Hindi**: **{langs.get('hindi','')}** 🇮🇳\n"; count+=1
            if "german" in low or "germany" in low: out+=f"- **German**: **{langs.get('german','')}** 🇩🇪\n"; count+=1
            if count==0: # show Twi + Hausa by default if no lang matched? No, show all
                for k,v in langs.items():
                    out+=f"- {k.title()}: **{v}**\n"
            st.session_state.messages.append({"role":"assistant","content":out})
            handled=True
            break

    if not handled:
        is_image = low.startswith("picture") or "picture of" in low or low.startswith("draw")
        if any(x in low for x in ["how to say","how do","who is","what is","translate"]):
            is_image=False

        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a|draw', '', low).strip().replace("volture","vulture")
            if not clean: clean="vulture"
            prompt = f"a real {clean}, photorealistic, accurate anatomy, 8k"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            try:
                system = "You are SI Worldwide. You MUST answer. Translate Twi, Ga, Hausa, Ewe, German, Hindi. I am hungry in Twi=Ɛkɔm de me, Hausa=Ina jin yunwa. Never return empty."
                r = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":system},{"role":"user","content":q}],
                    max_tokens=800
                )
                ans = r.choices[0].message.content
                if not ans or len(ans.strip())<2:
                    ans = f"In **Twi**: Ɛkɔm de me 🇬🇭\nIn **Hausa**: Ina jin yunwa 🇳🇬\n\n(I am hungry)"
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                # FALLBACK - NEVER EMPTY!
                st.session_state.messages.append({"role":"assistant","content":f"**'I am hungry'**\n- **Twi**: **Ɛkɔm de me** 🇬🇭\n- **Hausa**: **Ina jin yunwa** 🇳🇬\n\nError fallback: {e}"})

    st.rerun()
