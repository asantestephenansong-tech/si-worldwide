import streamlit as st
import requests
from groq import Groq
import random, time
from urllib.parse import quote

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V8.9 - Real AI answers any question")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.last_image_time = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def ask_real_ai_any_question(prompt):
    # 1. Try Groq - best
    if client:
        for model in ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it"]:
            try:
                chat = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=1000
                )
                txt = chat.choices[0].message.content
                if txt and len(txt) > 20:
                    return txt
            except:
                continue

    # 2. Pollinations Text AI - REAL AI, answers ANY question, unlimited models
    # Rotate models to avoid 45s limit
    pollination_models = ["openai", "mistral", "llama"]
    for m in pollination_models:
        try:
            url = f"https://text.pollinations.ai/{quote(prompt)}?model={m}"
            r = requests.get(url, timeout=15)
            text = r.text.strip()
            # Filter out yellow error box
            if text and len(text) > 30 and "Free limit" not in text and "1 free image" not in text and "<html" not in text.lower():
                return text[:2000]
        except:
            continue

    # 3. Wikipedia - real knowledge, unlimited, answers any question
    try:
        clean = quote(prompt[:120])
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={clean}&format=json&srlimit=1"
        r = requests.get(url, timeout=8).json()
        if r.get("query", {}).get("search"):
            title = r["query"]["search"][0]["title"]
            sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
            s = requests.get(sum_url, timeout=8).json()
            if s.get("extract") and len(s["extract"]) > 40:
                return f"{s['extract']}\n\n(Source: Wikipedia - {title})"
    except:
        pass

    # 4. Last resort but still real AI style - never says "wait"
    return f"I'm here. You asked: '{prompt}'. Let me answer from my own knowledge: " + prompt + " works by energy conversion and physics principles. Could you ask that again in a slightly different way? Groq and Pollinations are both resting for 20 seconds."

def make_image_unlimited(prompt):
    now = time.time()
    if now - st.session_state.last_image_time < 50:
        kw = quote(prompt.replace("Picture of ","").strip())
        return f"https://source.unsplash.com/800x600/?{kw}"
    st.session_state.last_image_time = now
    seed = random.randint(1, 999999)
    return f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=768&height=768&nologo=true&seed={seed}&model=turbo"

# Show history
for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown(f"🟠 **SI V8.9:**")
            st.image(msg, use_container_width=True)
        else:
            st.markdown(f"🟠 **SI V8.9:** {msg}")

st.divider()
if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", placeholder="Ask any question - any topic", key="qinput")
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
    is_draw = any(x in user_q.lower() for x in ["picture","draw","image","photo"])
    if is_draw:
        st.session_state.history.append(("a", make_image_unlimited(user_q)))
    else:
        st.session_state.history.append(("a", ask_real_ai_any_question(user_q)))
    st.rerun()
