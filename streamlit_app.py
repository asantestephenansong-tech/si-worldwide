import streamlit as st
import requests
from groq import Groq
import random, time
from urllib.parse import quote

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V11 - Up-to-date facts, real photos")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.last_image_time = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# LIVE FACTS INJECTION - Fixes old AI models
LIVE_FACTS = {
    "current pope": "The current Pope is Pope Leo XIV (Robert Francis Prevost). He was elected May 8, 2025, after Pope Francis died April 21, 2025. He is the first American Pope, born in Chicago.",
    "pope francis died": "Pope Francis died April 21, 2025 at age 88. He was succeeded by Pope Leo XIV.",
    "how many stones david": "David picked 5 smooth stones from the brook (1 Samuel 17:40), but used only 1 stone to strike Goliath down. The other 4 were backup."
}

def ask_anything(prompt):
    low = prompt.lower()
    
    # Check live facts first - always correct
    for key, fact in LIVE_FACTS.items():
        if key in low:
            return fact

    # 1. Groq
    if client:
        for model in ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it"]:
            try:
                c = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role":"system","content":"You are up to date: Pope Francis died April 21 2025, current Pope is Leo XIV since May 8 2025. David picked 5 stones, used 1. Current year is 2026."},
                        {"role":"user","content":prompt}
                    ],
                    max_tokens=1000
                )
                t = c.choices[0].message.content
                if t and len(t) > 20:
                    return t
            except:
                continue

    # 2. Pollinations fixed
    for m in ["openai", "mistral"]:
        try:
            url = f"https://text.pollinations.ai/{quote(prompt)}?model={m}&seed={random.randint(1,99999)}"
            r = requests.get(url, timeout=15)
            txt = r.text.strip()
            if txt.startswith("{") and '"error"' in txt: 
                continue
            if txt and len(txt) > 30 and "Free limit" not in txt and "<html" not in txt.lower():
                return txt[:2000]
        except:
            continue

    # 3. Wikipedia/DuckDuckGo
    try:
        d = requests.get(f"https://api.duckduckgo.com/?q={quote(prompt)}&format=json&pretty=1", timeout=8).json()
        if d.get("AbstractText") and len(d["AbstractText"]) > 40:
            return d["AbstractText"][:1500]
    except:
        pass

    return f"Answering '{prompt}' - please wait 3 seconds and ask again, servers busy."

def make_image(prompt):
    now = time.time()
    # Use more realistic prompt
    realistic_prompt = prompt + ", realistic photo, natural lighting, high detail"
    if now - st.session_state.last_image_time < 50:
        kw = quote(prompt.replace("Picture of ","").strip())
        return f"https://source.unsplash.com/800x600/?{kw},real,person"
    st.session_state.last_image_time = now
    return f"https://image.pollinations.ai/prompt/{quote(realistic_prompt)}?width=768&height=768&nologo=true&seed={random.randint(1,999999)}&model=turbo"

for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V11:**")
            st.image(msg, use_container_width=True)
        else:
            st.markdown(f"🟠 **SI V11:** {msg}")

st.divider()
if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", key="qinput")
c1,c2 = st.columns([4,1])
with c1:
    send = st.button("Send ✨", type="primary", use_container_width=True)
with c2:
    clr = st.button("Clear", use_container_width=True)

if clr:
    st.session_state.history = []
    st.rerun()

if send and q and q.strip():
    user_q = q.strip()
    st.session_state.history.append(("u", user_q))
    st.session_state.clear_input = True
    if any(x in user_q.lower() for x in ["picture","draw","image","photo"]):
        st.session_state.history.append(("a", make_image(user_q)))
    else:
        st.session_state.history.append(("a", ask_anything(user_q)))
    st.rerun()
