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
st.caption("V7.1 - Stable Ghana AI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Type here", placeholder="Ex: Picture of a vulture or Let's go home in Ga")
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and text.strip():
    q = text.strip()
    low = q.lower()

    # BLOCK DUPLICATE
    last = [m for m in st.session_state.messages if m["role"]=="user"]
    if last and last[-1]["content"] == q:
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})

    DICT = {
        "let's go home": {"ga":"Tee wɔ shia", "twi":"Momma yɛnkɔ fie", "german":"Lass uns nach Hause gehen", "hindi":"Chalo ghar chalte hain"},
        "go and sleep": {"ga":"Tee ya wɔ", "twi":"Kɔ bɛda", "german":"Geh und schlaf", "hindi":"Jao aur so jao"},
        "go home": {"ga":"Tee shia", "twi":"Kɔ fie", "german":"Geh nach Hause", "hindi":"Ghar jao"},
        "boys fighting": {"desc":"boys boxing"},
    }

    handled=False
    for phrase in sorted(DICT.keys(), key=len, reverse=True):
        if phrase in low and phrase!="boys fighting":
            langs = DICT[phrase]
            out=f"**'{phrase}'** means:\n\n"
            if "ga" in low or re.search(r'\bga\b', low): out+=f"- **Ga**: **{langs.get('ga')}** 🇬🇭\n"
            if "twi" in low: out+=f"- **Twi**: **{langs.get('twi')}** 🇬🇭\n"
            if "german" in low or "germany" in low: out+=f"- **German**: **{langs.get('german')}** 🇩🇪\n"
            if "hindi" in low: out+=f"- **Hindi**: **{langs.get('hindi')}** 🇮🇳\n"
            if out.count("-")==0:
                for k,v in langs.items(): out+=f"- {k}: {v}\n"
            st.session_state.messages.append({"role":"assistant","content":out})
            handled=True
            break

    if not handled:
        is_image = low.startswith("picture") or "picture of" in low or low.startswith("draw")
        if any(x in low for x in ["how do","how to","who is","what is","say"]):
            is_image=False

        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a|draw', '', low).strip().replace("volture","vulture")
            if not clean: clean="vulture"
            prompt = f"{clean}, photorealistic, 8k, accurate"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            r = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":"You are SI Worldwide. Translate full phrases, know Ga, Twi, German, Hindi. Never shorten let's go home to go home."},{"role":"user","content":q}],
                max_tokens=700
            )
            st.session_state.messages.append({"role":"assistant","content":r.choices[0].message.content})
    st.rerun()
