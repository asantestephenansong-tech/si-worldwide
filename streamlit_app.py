import streamlit as st
import requests, random, time
from groq import Groq

st.set_page_config(page_title="SI Worldwide V16", page_icon="🌍", layout="wide")

groq_key = st.secrets.get("GROQ_API_KEY")
poll_key = st.secrets.get("POLLINATIONS_API_KEY", "")
client = Groq(api_key=groq_key)

# WORKING MODELS in 2026 - llama 3.3 is Enterprise only now
MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]

SYSTEM = """You are SI Worldwide AI V16 by Stephen Asante, Oct 2026.
Remember previous chat. Answer in same language user uses.
Pope Leo XIV, US President Donald Trump, Ghana President John Mahama.
For images, say 'AI illustration'.
"""

st.markdown("""
<style>
.main .block-container {max-width: 100% !important; padding-top: 1rem}
[data-testid="stChatMessages"] {height: calc(100vh - 180px) !important}
</style>
""", unsafe_allow_html=True)

st.title("🌍 SI Worldwide V16")
st.caption("Fix: Groq + Pollinations limit")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_img" not in st.session_state:
    st.session_state.last_img = 0

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"])
            st.caption("AI illustration, not real photo")
        else:
            st.markdown(m["content"])

prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role":"user","type":"text","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    is_img = any(k in prompt.lower() for k in ["picture","image","photo","draw","generate"])
    
    with st.chat_message("assistant"):
        if is_img:
            safe = prompt.lower()
            for w in ["picture of a","picture of","image of","photo of","generate","draw","picture"]:
                safe = safe.replace(w, " ")
            safe = " ".join(safe.split()).strip() or "landscape"

            if not poll_key:
                wait = 45 - (time.time() - st.session_state.last_img)
                if wait > 0:
                    st.warning(f"⏳ Free image limit - wait {int(wait)}s or add POLLINATIONS_API_KEY for unlimited")
                    time.sleep(wait+1)

            seed = random.randint(1,9999999)
            enc = requests.utils.quote(safe)
            token = f"&token={poll_key}" if poll_key else ""
            # Use turbo - faster and less limited than flux
            url = f"https://image.pollinations.ai/prompt/{enc}?width=1024&height=1024&model=turbo&seed={seed}&nologo=true{token}"
            
            st.image(url, caption=safe)
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
            st.session_state.last_img = time.time()
        else:
            # Memory - last 8 messages
            history = [{"role":"system","content":SYSTEM}]
            for mm in st.session_state.messages[-8:]:
                if mm.get("type") != "image":
                    history.append({"role": mm["role"], "content": mm["content"]})

            answer = None
            for model in MODELS:
                try:
                    comp = client.chat.completions.create(model=model, messages=history, max_tokens=900)
                    answer = comp.choices[0].message.content
                    break
                except Exception as e:
                    if "model_not_found" not in str(e).lower():
                        answer = f"Error: {e}"
                        break
                    continue
            
            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role":"assistant","type":"text","content":answer})
            else:
                st.error("All models busy - try again in 10 sec")
