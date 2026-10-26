import streamlit as st
import requests
from groq import Groq
import random
from urllib.parse import quote

# SAFETY + CURRENT INFO
BLOCKED_WORDS = ["school girl", "school boy", "schoolboy", "schoolgirl", "messi", "ronaldo", "shatta wale", "stonebwoy", "sarkodie", "john mahama", "donald trump", "elon musk"]

def is_blocked(prompt):
    p = prompt.lower()
    return any(w in p for w in BLOCKED_WORDS) or "picture of" in p and any(name in p for name in ["messi","ronaldo","shatta","mahama","trump","musk","child","kid","boy","girl"])

SYSTEM_PROMPT = """You are SI V14. Today is October 2026.
Current facts you MUST use:
- Pope is Leo XIV (since May 2025), not Francis
- US President is Donald Trump (since Jan 2025)
- Ghana President is John Mahama (since Jan 2025)
- You are SI Worldwide AI built by Stephen Asante
Never say you are Pollinations or Pollen.
If user asks for picture of real person or child, refuse and offer generic alternative.
Keep answers short, helpful, and friendly. Use same language as user.
"""

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V14 - Answers ANY question you throw at me - No timeout")

# KEYS - THIS FIXES FREE LIMIT
GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_KEY = st.secrets.get("HF_API_KEY", "")
POLLEN_KEY = st.secrets.get("POLLEN_API_KEY", "")

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []

def ask_any_question(prompt):
    # STREAMING - NO TIMEOUT EVER
    if client:
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.history[-6:],
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                max_tokens=1200,
                temperature=0.7
            )
            full_text = ""
            placeholder = st.empty()
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_text += content
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            return full_text
        except Exception as e:
            return f"Groq error: {e}. Check your GROQ_API_KEY in Secrets."
    else:
        return "⚠️ GROQ_API_KEY missing. Add it in Manage app > Secrets > GROQ_API_KEY = 'gsk_...'"

def make_image(prompt):
    if is_blocked(prompt):
        st.error("❌ I can't generate images of real people like Messi, Shatta Wale, or children. Try: 'a football player celebrating' or 'a Ghanaian musician on stage'.")
        return None
    
    try:
        encoded = quote(prompt[:200])
        # Pollinations IMAGE only
        url = f"https://image.pollinations.ai/prompt/{encoded}?nologo=true&private=true&enhance=true"
        if POLLEN_KEY:
            url += f"&key={POLLEN_KEY}"
        return url
    except Exception as e:
        st.error(f"Image error: {e}")
        return None

# CHAT UI
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    # Check if image request
    is_image = any(k in user_input.lower() for k in ["picture", "image", "draw", "generate", "photo"])

    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        if is_image:
            img_url = make_image(user_input)
            if img_url:
                st.image(img_url, caption=user_input)
                st.session_state.history.append({"role": "assistant", "content": f"Image: {user_input}"})
        else:
            answer = ask_any_question(user_input)
            st.session_state.history.append({"role": "assistant", "content": answer})
