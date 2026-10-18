import streamlit as st
import requests
from groq import Groq
import random, time

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V8.4 - 45s limit fixed")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
if "last_image_time" not in st.session_state:
    st.session_state.last_image_time = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def ask_fast(prompt):
    if client:
        try:
            chat = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":prompt}],
                max_tokens=500
            )
            return chat.choices[0].message.content
        except:
            pass
    try:
        r = requests.get(f"https://text.pollinations.ai/{prompt}", timeout=20)
        if "Free limit" not in r.text and len(r.text) > 20:
            return r.text[:1500]
    except:
        pass
    return "⏳ Text limit, wait 30 sec and retry."

def make_image_smart(prompt):
    # Enforce Pollinations rule
    now = time.time()
    elapsed = now - st.session_state.last_image_time
    if elapsed < 50:  # 50 sec to be safe
        return f"WAIT_{int(50-elapsed)}"
    
    seed = random.randint(1, 999999)
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&nologo=true&seed={seed}&model=turbo"
    st.session_state.last_image_time = now
    return url

# Show history
for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V8.4:**")
            st.image(msg, use_container_width=True)
        elif msg.startswith("WAIT_"):
            secs = msg.split("_")[1]
            st.warning(f"⏳ Please wait {secs} seconds. Pollinations allows 1 image per 45s. Try again after.")
        else:
            st.markdown(f"🟠 **SI V8.4:** {msg}")

st.divider()

if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", placeholder="Ask anything or ask for picture", key="qinput")
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
    
    is_draw = any(x in user_q.lower() for x in ["picture","draw","image","photo","messi","jackson","mouse"])
    
    if is_draw:
        img = make_image_smart(user_q)
        st.session_state.history.append(("a", img))
    else:
        ans = ask_fast(user_q)
        st.session_state.history.append(("a", ans))
    st.rerun()
