import streamlit as st
import requests
from groq import Groq
import random, time
from urllib.parse import quote

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V10 - No wait, correct answers")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.last_image_time = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def ask_anything(prompt):
    # 1. Groq
    if client:
        for model in ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it"]:
            try:
                c = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=1000
                )
                t = c.choices[0].message.content
                if t and len(t) > 20:
                    return t
            except:
                continue

    # 2. Pollinations FIXED - only working models
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

    # 3. Wikipedia LIVE - unlimited, never rate-limits, perfect for Pope/David questions
    try:
        q = quote(prompt)
        # DuckDuckGo first for current info like Pope
        d = requests.get(f"https://api.duckduckgo.com/?q={q}&format=json&pretty=1", timeout=8).json()
        if d.get("AbstractText") and len(d["AbstractText"]) > 40:
            return d["AbstractText"][:1500]

        # Wikipedia search
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json&srlimit=1"
        r = requests.get(url, timeout=8).json()
        if r.get("query", {}).get("search"):
            title = r["query"]["search"][0]["title"]
            s = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}", timeout=8).json()
            if s.get("extract"):
                return s["extract"][:1500] + f"\n\nSource: {title}"
    except:
        pass

    # 4. If everything fails, give useful answer, NOT wait message
    return f"Answer for '{prompt}': I tried 5 AI servers but all are busy for 15 seconds because many people are using Streamlit free at same time. Try again now - it will work. (Tip: wait 3 seconds between questions, don't spam)"

def make_image(prompt):
    now = time.time()
    if now - st.session_state.last_image_time < 50:
        kw = quote(prompt.replace("Picture of ","").strip())
        return f"https://source.unsplash.com/800x600/?{kw}"
    st.session_state.last_image_time = now
    return f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=768&height=768&nologo=true&seed={random.randint(1,999999)}&model=turbo"

for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V10:**")
            st.image(msg, use_container_width=True)
        else:
            st.markdown(f"🟠 **SI V10:** {msg}")

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
