import streamlit as st
import requests
from groq import Groq

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")
st.title("🌍 SI Worldwide AI")
st.caption("V8.2 - Fast & Fixed")

# --- KEYS ---
GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# --- CORE FUNCTIONS ---
def ask_fast(prompt):
    # 1. Groq (primary)
    if client:
        try:
            chat = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return chat.choices[0].message.content
        except Exception as e:
            print(f"Groq failed: {e}")
            pass

    # 2. Pollinations backup - works WITHOUT key
    try:
        r = requests.get(
            f"https://text.pollinations.ai/{prompt}",
            params={"model": "openai"},
            timeout=20
        )
        if r.status_code == 200 and len(r.text.strip()) > 10:
            return r.text[:1500]
    except:
        pass

    # 3. Second Pollinations endpoint
    try:
        r = requests.get(f"https://text.pollinations.ai/{prompt}", timeout=15)
        if r.status_code == 200 and len(r.text.strip()) > 10:
            return r.text[:1500]
    except:
        pass

    return "Groq is busy (free limit). Wait 60 seconds and try again - it auto-recovers!"

def make_image_fast(prompt):
    # Add random seed so different images
    seed = hash(prompt + str(len(st.session_state.history))) % 999999
    return f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&nologo=true&seed={seed}"

# --- SHOW CHAT HISTORY ---
for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if isinstance(msg, str) and msg.startswith("http"):
            st.markdown("🟠 **SI V8.2:**")
            st.image(msg, use_container_width=True)
        else:
            st.markdown(f"🟠 **SI V8.2:** {msg}")

st.divider()

# --- INPUT BAR WITH FIX ---
# This clears the bar after send
if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", placeholder="Ask anything, or ask for picture", key="qinput")

col1, col2 = st.columns([4, 1])
with col1:
    send = st.button("Send ✨", type="primary", use_container_width=True)
with col2:
    clr = st.button("Clear", use_container_width=True)

if clr:
    st.session_state.history = []
    st.session_state.qinput = ""
    st.rerun()

if send and q and q.strip():
    user_q = q.strip()
    
    # Save user message
    st.session_state.history.append(("u", user_q))
    
    # MARK FOR CLEARING - This fixes your screenshot issue
    st.session_state.clear_input = True

    # Check if wants image
    is_draw = any(x in user_q.lower() for x in ["picture", "draw", "image", "photo", "generate", "create", "messi", "ronaldo", "vulture", "lion", "cat", "dog"])

    if is_draw:
        with st.spinner("Drawing fast..."):
            img_url = make_image_fast(user_q)
            st.session_state.history.append(("a", img_url))
    else:
        with st.spinner("Thinking..."):
            ans = ask_fast(user_q)
            st.session_state.history.append(("a", ans))

    st.rerun()
