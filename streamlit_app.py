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

st.title("SI Worldwide 🌍")
st.caption("V7.0 - No Repeat Final")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

# USE FORM = NO REPEAT!
with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Type here", placeholder="Ex: go and sleep in Hindi")
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and text.strip():
    to_answer = text.strip()
    low = to_answer.lower()

    # BLOCK DUPLICATE - If same as last user message, ignore
    last_users = [m["content"] for m in st.session_state.messages if m["role"]=="user"]
    if last_users and last_users[-1] == to_answer:
        st.stop()

    st.session_state.messages.append({"role":"user","content":to_answer})

    DICT = {
        "go and sleep": {"twi":"Kɔ bɛda", "ga":"Tee ya wɔ", "ewe":"Yi dɔ alɔ", "hindi":"Jao aur so jao", "german":"Geh und schlaf"},
        "go home": {"twi":"Kɔ fie", "ga":"Tee shia", "ewe":"Yi afeme", "hindi":"Ghar jao", "german":"Geh nach Hause"},
        "bring it": {"twi":"Fa bra", "ga":"Kɛ lɛ ba", "hindi":"Ise lao", "german":"Bring es"},
    }

    handled=False
    for phrase in sorted(DICT.keys(), key=len, reverse=True):
        if phrase in low:
            langs = DICT[phrase]
            out=f"**'{phrase}'** means:\n\n"
            if "twi" in low: out+=f"- Twi: **{langs.get('twi')}** 🇬🇭\n"
            if re.search(r'\bga\b', low): out+=f"- Ga: **{langs.get('ga')}** 🇬🇭\n"
            if "hindi" in low: out+=f"- Hindi: **{langs.get('hindi')}** 🇮🇳\n"
            if "german" in low or "germany" in low: out+=f"- German: **{langs.get('german')}** 🇩🇪\n"
            if "french" in low: out+=f"- French: {langs.get('french','')}\n"
            if out.count("-")==0:
                for k,v in langs.items(): out+=f"- {k}: {v}\n"
            st.session_state.messages.append({"role":"assistant","content":out})
            handled=True
            break

    if not handled:
        is_image = low.startswith("picture") or "picture of" in low or low.startswith("draw")
        if any(x in low for x in ["who is","what is","how do","how to","how many"]):
            is_image=False
        if is_image:
            clean = re.sub(r'picture of a|picture of|draw', '', low).strip().replace("volture","vulture")
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean)}?width=1024&height=1024&nologo=true&model=flux"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            r = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":"You are SI Worldwide, translate full phrases."},{"role":"user","content":to_answer}],
                max_tokens=600
            )
            st.session_state.messages.append({"role":"assistant","content":r.choices[0].message.content})
    st.rerun()
