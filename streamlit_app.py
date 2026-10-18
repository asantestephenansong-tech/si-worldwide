import streamlit as st
import requests
from groq import Groq
import time

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []

# --- FAST FUNCTIONS ---
def ask_fast(prompt):
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":prompt}],
            max_tokens=200
        )
        return chat.choices[0].message.content
    except:
        try:
            r = requests.get(f"https://text.pollinations.ai/{prompt}", timeout=10)
            return r.text[:500]
        except:
            return "Network slow, try again."

def make_image_fast(prompt):
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true"
        return url
    except:
        return None

# --- SHOW CHAT ---
for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V8.0:** Here is your picture:")
            st.image(msg)
        else:
            st.markdown(f"🟠 **SI V8.0:** {msg}")

st.divider()

# --- INPUT BAR ---
q = st.text_input("Ask...", placeholder="Ask anything", key="qinput")
c1,c2 = st.columns([4,1])
with c1:
    send = st.button("Send ✨", type="primary", use_container_width=True)
with c2:
    clr = st.button("Clear", use_container_width=True)

if clr:
    st.session_state.history = []
    if "qinput" in st.session_state:
        del st.session_state["qinput"]
    st.rerun()

if send and q:
    # 1. Save question
    st.session_state.history.append(("u", q))
    user_q = q
    
    # 2. *** THIS FIXES YOUR PROBLEM: Clear the bar ***
    if "qinput" in st.session_state:
        del st.session_state["qinput"]
    
    # 3. Answer
    is_draw = any(x in user_q.lower() for x in ["picture","draw","image","photo","messi","ronaldo"])
    
    if is_draw:
        with st.spinner("Drawing..."):
            img = make_image_fast(user_q)
            st.session_state.history.append(("a", img))
    else:
        with st.spinner("Thinking..."):
            ans = ask_fast(user_q)
            st.session_state.history.append(("a", ans))
    
    # 4. Reload with empty bar
    st.rerun()
