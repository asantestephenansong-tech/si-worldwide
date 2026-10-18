import streamlit as st
import requests
from groq import Groq

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def ask_fast(prompt):
    if client:
        try:
            chat = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":f"Answer short: {prompt}"}],
                max_tokens=300
            )
            return chat.choices[0].message.content
        except Exception as e:
            pass
    try:
        r = requests.get(f"https://text.pollinations.ai/{prompt}", timeout=15)
        if r.status_code == 200:
            return r.text[:800]
    except:
        pass
    return "I could not connect. Check GROQ_API_KEY in Secrets, then Reboot app."

def make_image_fast(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&nologo=true&seed={hash(prompt)%1000}"

# Show chat
for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V8.1:** Here is your picture:")
            st.image(msg)
        else:
            st.markdown(f"🟠 **SI V8.1:** {msg}")

st.divider()

# INPUT - THIS IS THE FIX FOR YOUR SCREENSHOT
if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", placeholder="Ask anything", key="qinput")
c1,c2 = st.columns([4,1])
with c1:
    send = st.button("Send ✨", type="primary", use_container_width=True)
with c2:
    clr = st.button("Clear", use_container_width=True)

if clr:
    st.session_state.history = []
    st.session_state.qinput = ""
    st.rerun()

if send and q and q.strip():
    user_q = q.strip()
    st.session_state.history.append(("u", user_q))
    # CLEAR BAR NOW - BEFORE ANSWERING
    st.session_state.clear_input = True
    
    is_draw = any(x in user_q.lower() for x in ["picture","draw","image","photo","vulture","messi","ronaldo"])
    
    if is_draw:
        with st.spinner("Drawing..."):
            img = make_image_fast(user_q)
            st.session_state.history.append(("a", img))
    else:
        with st.spinner("Thinking..."):
            ans = ask_fast(user_q)
            st.session_state.history.append(("a", ans))
    
    st.rerun()
