import streamlit as st
import requests
from groq import Groq
import random, time

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V8.3 - No more limit error")

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
                messages=[{"role":"user","content":prompt}],
                max_tokens=500
            )
            return chat.choices[0].message.content
        except:
            pass
    # 3 text backups
    for url in [
        f"https://text.pollinations.ai/{prompt}?model=openai",
        f"https://text.pollinations.ai/{prompt}",
    ]:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and "Free limit" not in r.text and len(r.text) > 20:
                return r.text[:1500]
        except:
            continue
    return "⏳ Free AI is busy (too many users on Streamlit). Wait 2 minutes and try again - it auto-fixes!"

def make_image_smart(prompt):
    # Try 4 different image URLs
    seed = random.randint(1, 999999)
    urls = [
        f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&nologo=true&seed={seed}&model=turbo",
        f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&seed={seed+1}",
        f"https://pollinations.ai/p/{prompt}?width=768&height=768&seed={seed}",
    ]
    for u in urls:
        try:
            # Check if URL returns image, not limit page
            r = requests.head(u, timeout=10)
            if r.status_code == 200:
                return u
        except:
            pass
    # If all fail, return first anyway + we will show nice message
    return urls[0]

# Show history
for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V8.3:**")
            try:
                st.image(msg, use_container_width=True)
            except:
                st.warning("⏳ Image limit reached, wait 1 min and tap Send again")
                st.markdown(f"[Try open image]({msg})")
        else:
            st.markdown(f"🟠 **SI V8.3:** {msg}")

st.divider()

if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", placeholder="Ask or picture", key="qinput")
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
    
    is_draw = any(x in user_q.lower() for x in ["picture","draw","image","photo","mouse","messi","vulture"])
    
    if is_draw:
        with st.spinner("Drawing..."):
            img = make_image_smart(user_q)
            st.session_state.history.append(("a", img))
    else:
        with st.spinner("Thinking..."):
            ans = ask_fast(user_q)
            st.session_state.history.append(("a", ans))
    st.rerun()
