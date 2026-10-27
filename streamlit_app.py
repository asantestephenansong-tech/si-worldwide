import streamlit as st
import requests
from groq import Groq
from datetime import datetime
import time, random

st.set_page_config(page_title="SI Worldwide AI V16", page_icon="🌍", layout="centered")

groq_key = st.secrets.get("GROQ_API_KEY")
poll_key = st.secrets.get("POLLINATIONS_API_KEY", "")

client = Groq(api_key=groq_key)

BLOCKED = ["child porn", "nude child", "sex with child", "school girl nude"]
def is_blocked(p): return any(w in p.lower() for w in BLOCKED)

SYSTEM_PROMPT = """You are SI Worldwide AI V16 built by Stephen Asante.
Today: Oct 2026. Pope Leo XIV (since May 8 2025), US President Donald Trump (since Jan 20 2025), Ghana President John Mahama.
You are SI Worldwide AI V16. Never say Pollinations. For public figures you CAN generate image as AI illustration.
Remember previous conversation. Answer in same language user uses.
"""

st.title("🌍 SI Worldwide AI V16")
st.caption("Unlimited + Memory + No Timeout")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_img" not in st.session_state:
    st.session_state.last_img = 0

# Show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):

    if is_blocked(prompt):
        st.warning("Can't generate that for safety."); st.stop()

    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    is_image = any(k in prompt.lower() for k in ["picture", "image", "photo", "draw", "generate"])

    with st.chat_message("assistant"):
        if is_image:
            safe = prompt.lower()
            for r in ["picture of", "image of", "photo of", "picture", "generate", "draw", "of"]:
                safe = safe.replace(r, " ")
            safe = " ".join(safe.split()).strip()
            if len(safe) < 2: safe = prompt

            seed = random.randint(1, 9999999)
            encoded = requests.utils.quote(safe)
            token_param = f"&token={poll_key}" if poll_key else ""

            if not poll_key:
                wait = 45 - (time.time() - st.session_state.last_img)
                if wait > 0:
                    st.warning(f"⏳ Free limit: wait {int(wait)}s. Add POLLINATIONS_API_KEY for unlimited.")
                    time.sleep(wait+1)

            # Use with token for unlimited
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&seed={seed}&nologo=true&enhance=true{token_param}"
            
            try:
                # Test if limit error
                resp = requests.head(image_url, timeout=10)
                st.image(image_url, caption=f"AI illustration: {safe}")
                st.caption("AI illustration, not a real photo.")
                st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_url})
                st.session_state.last_img = time.time()
            except Exception as e:
                st.error(f"Pollinations busy. {'Add API key for unlimited' if not poll_key else 'Try again in 10 sec'}")
        else:
            # --- WITH MEMORY FIX ---
            MODELS = ["llama-3.3-70b-versatile", "gemma2-9b-it", "openai/gpt-oss-20b"]
            answer = None
            
            # Build history for Groq so it remembers "what about in French"
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            # Add last 6 messages as memory
            for m in st.session_state.messages[-6:]:
                if m.get("type") != "image":
                    history.append({"role": m["role"], "content": m["content"]})
            
            for m in MODELS:
                try:
                    comp = client.chat.completions.create(model=m, messages=history, temperature=0.6, max_tokens=1000)
                    answer = comp.choices[0].message.content
                    break
                except: continue
            
            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": answer})
            else:
                st.error("Groq error - check API key")
