import streamlit as st
import requests, random, time
from groq import Groq

st.set_page_config(page_title="SI Worldwide V16", page_icon="🌍", layout="wide")

# --- SECRETS ---
groq_key = st.secrets.get("GROQ_API_KEY")
poll_key = st.secrets.get("POLLINATIONS_API_KEY", "")
client = Groq(api_key=groq_key)

SYSTEM = """You are SI Worldwide AI V16 by Stephen Asante, Oct 2026.
Pope Leo XIV since May 8 2025, US President Donald Trump since Jan 20 2025, Ghana President John Mahama.
Remember conversation history. Answer in same language user uses. For images, say 'AI illustration'.
"""

# --- FULL SCREEN CSS ---
st.markdown("""
<style>
.main .block-container {max-width: 100% !important; padding-top: 1rem; height: 100vh}
[data-testid="stChatMessages"] {height: calc(100vh - 180px) !important}
header, footer {visibility: hidden}
</style>
""", unsafe_allow_html=True)

st.title("🌍 SI Worldwide V16 - Forever Alive")
st.caption("19 viewers | Unlimited images when key added | With memory")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_img" not in st.session_state:
    st.session_state.last_img = 0

# Show chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""))
            st.caption("AI illustration, not real photo")
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Ask anything... 'picture of messi' or 'sleep in Twi'")
if prompt:
    st.session_state.messages.append({"role":"user","type":"text","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    is_img = any(k in prompt.lower() for k in ["picture","image","photo","draw","generate"])

    with st.chat_message("assistant"):
        if is_img:
            # Clean prompt
            safe = prompt.lower()
            for w in ["picture of a","picture of","image of","photo of","generate","draw a","draw","picture","of"]:
                safe = safe.replace(w, " ")
            safe = " ".join(safe.split()).strip() or "beautiful landscape"

            # Check 45s free limit
            if not poll_key:
                wait = 45 - (time.time() - st.session_state.last_img)
                if wait > 0:
                    st.warning(f"⏳ Free tier limit: wait {int(wait)}s. Add POLLINATIONS_API_KEY in Secrets for unlimited.")
                    time.sleep(wait+1)

            seed = random.randint(1,9999999)
            enc = requests.utils.quote(safe)
            token = f"&token={poll_key}" if poll_key else ""
            url = f"https://image.pollinations.ai/prompt/{enc}?width=1024&height=1024&model=turbo&seed={seed}&nologo=true&enhance=true{token}"

            try:
                st.image(url, caption=f"AI illustration: {safe}")
                st.caption("AI illustration, not a real photo.")
                st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":safe})
                st.session_state.last_img = time.time()
            except:
                st.error("Pollinations busy at this second. Try again in 10s or add API key for unlimited.")
        else:
            # MEMORY FIX - send last 8 messages
            history = [{"role":"system","content":SYSTEM}]
            for mm in st.session_state.messages[-8:]:
                if mm.get("type") != "image":
                    history.append({"role": mm["role"], "content": mm["content"]})
            history.append({"role":"user","content":prompt})

            try:
                comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=history, max_tokens=900, temperature=0.6)
                ans = comp.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","type":"text","content":ans})
            except Exception as e:
                st.error(f"Groq error: {e}")
