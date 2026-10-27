import streamlit as st
import requests
from groq import Groq
from datetime import datetime
import time
import random

st.set_page_config(page_title="SI Worldwide AI V15", page_icon="🌍", layout="centered")

# --- SECRETS - SET ONCE, NEVER CHANGE DAILY ---
# Add these in Streamlit > Manage app > Settings > Secrets:
# GROQ_API_KEY = "gsk_...."
# POLLINATIONS_API_KEY = "pk_..."  <-- from pollinations.ai

groq_key = st.secrets.get("GROQ_API_KEY")
poll_key = st.secrets.get("POLLINATIONS_API_KEY", "")

if not groq_key:
    st.error("Add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

client = Groq(api_key=groq_key)

# --- SAFETY ---
BLOCKED = ["child porn", "nude child", "sex with child", "school girl nude", "school boy nude"]
def is_blocked(p): return any(w in p.lower() for w in BLOCKED)

SYSTEM_PROMPT = f"""You are SI Worldwide AI V15 built by Stephen Asante. Today is {datetime.now().strftime('%B %Y')}.
- Pope is Leo XIV (since May 8 2025), US President is Donald Trump (since Jan 20 2025), Ghana President is John Mahama (since Jan 7 2025)
- You are SI Worldwide AI V15. Never say you are Pollinations, Pollen, OpenAI.
- For public figures like Elon Musk, Messi, Shatta Wale you CAN generate image as AI illustration.
- Keep answers short, friendly.
"""

# --- UI ---
st.title("🌍 SI Worldwide AI V15")
st.caption("Unlimited Images + No Timeout")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_img" not in st.session_state:
    st.session_state.last_img = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything... e.g. picture of elon musk"):

    if is_blocked(prompt):
        with st.chat_message("assistant"):
            st.warning("Can't generate that for safety.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    is_image = any(k in prompt.lower() for k in ["picture of", "image of", "photo of", "draw", "generate image", "picture"])

    with st.chat_message("assistant"):
        if is_image:
            safe = prompt.lower()
            for r in ["picture of", "image of", "photo of", "generate image of", "generate image", "picture", "draw"]:
                safe = safe.replace(r, "")
            safe = safe.strip()
            if len(safe) < 3:
                safe = prompt

            seed = random.randint(1, 9999999)
            encoded = requests.utils.quote(safe)

            # --- UNLIMITED WITH KEY ---
            # If poll_key exists, no more 45 sec limit
            token_param = f"&token={poll_key}" if poll_key else ""
            
            # Only enforce 45 sec wait if NO key
            if not poll_key:
                wait = 45 - (time.time() - st.session_state.last_img)
                if wait > 0:
                    st.warning(f"⏳ Free Pollinations = 1 image/45 sec. Wait {int(wait)}s or add POLLINATIONS_API_KEY for unlimited.")
                    time.sleep(wait + 1)

            urls = [
                f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux&seed={seed}{token_param}",
                f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=turbo&seed={seed}{token_param}"
            ]

            shown = False
            for url in urls:
                try:
                    st.image(url, caption=f"AI illustration: {safe}")
                    st.caption("This is an AI illustration, not a real photo.")
                    st.session_state.messages.append({"role": "assistant", "type": "image", "content": url})
                    st.session_state.last_img = time.time()
                    shown = True
                    break
                except:
                    continue
            
            if not shown:
                st.error("Image failed. If you have no key, wait 45 sec. If you added key, check key in Secrets.")

        else:
            # --- GROQ WITH AUTO FALLBACK - NEVER 404 ---
            MODELS = ["llama-3.3-70b-versatile", "gemma2-9b-it", "openai/gpt-oss-20b", "llama-3.1-8b-instant"]
            answer = None
            for m in MODELS:
                try:
                    comp = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    answer = comp.choices[0].message.content
                    break
                except Exception as e:
                    continue

            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": answer})
            else:
                st.error("Groq failed. Check GROQ_API_KEY in Secrets. Key may be revoked if exposed on GitHub.")
