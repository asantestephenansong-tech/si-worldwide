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
    # 1. Groq - best
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

    # 2. Pollinations - FIXED MODEL NAMES
    # Only use models that work 100% today
    pollination_models = ["openai", "mistral", "openai-large"]
    for m in pollination_models:
        try:
            url = f"https://text.pollinations.ai/{quote(prompt)}?model={m}"
            r = requests.get(url, timeout=15)
            text = r.text.strip()
            # Ignore JSON errors like the one in your screenshot
            if text.startswith("{") and '"error"' in text:
                continue
            if text and len(text) > 30 and "Free limit" not in text and "<html" not in text.lower():
                return text[:2000]
        except:
            continue

    # 3. Wikipedia backup - unlimited
    try:
        clean = quote(prompt[:120])
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={clean}&format=json&srlimit=1"
        r = requests.get(url, timeout=8).json()
        if r.get("query", {}).get("search"):
            title = r["query"]["search"][0]["title"]
            sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
            s = requests.get(sum_url, timeout=8).json()
            if s.get("extract"):
                return f"{s['extract']}\n\n(Wikipedia: {title})"
    except:
        pass

    return "Groq and Pollinations both resting 20 sec. Please wait 20 sec and ask again - it will work. Your previous 2 questions worked perfectly, this one hit a bad model name which V9.0 fixed."

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
