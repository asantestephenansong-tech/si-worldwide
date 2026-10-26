import streamlit as st
import requests
from groq import Groq
import random
from urllib.parse import quote

# SAFETY + CURRENT INFO
BLOCKED_WORDS = ["school girl", "school boy", "messi", "mahama", "ronaldo", "trump", "biden", "nude", "sex", "fight", "child", "pope"]
def is_blocked(prompt):
    return any(w in prompt.lower() for w in BLOCKED_WORDS)

SYSTEM_PROMPT = """You are SI V14. Today is October 2026.
Current facts you MUST use:
- Pope is Leo XIV (since May 2025), not Francis
- US President is Donald Trump (since Jan 2025)
- Ghana President is John Mahama (since Jan 2025)
Never say you are Pollinations or Pollen.
If user asks for picture of real person or child, refuse safely.
"""

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V14 - Answers ANY question you throw")

# KEYS - THIS FIXES FREE LIMIT
GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_KEY = st.secrets.get("HF_API_KEY", "")
POLLEN_KEY = st.secrets.get("POLLEN_API_KEY", "")

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []

def ask_any_question(prompt):
    # 1. Try Groq first
    if client:
        for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            try:
                c = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1200
                )
                return c.choices[0].message.content
            except:
                continue
    # 2. Pollinations text with SK key
    try:
        headers = {"Authorization": f"Bearer {POLLEN_KEY}"} if POLLEN_KEY else {}
        r = requests.post(
            "https://text.pollinations.ai/openai",
            headers=headers,
            json={"model": "openai", "messages": [{"role": "user", "content": prompt}], "system": SYSTEM_PROMPT},
            timeout=30
        )
        if r.ok:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"
    return "Please add your sk_... key in Secrets and Reboot."

def gen_image_url(prompt):
    if is_blocked(prompt):
        return None
    enc = quote(prompt)
    # Use new gen server + key
    key_part = f"&key={POLLEN_KEY}" if POLLEN_KEY else ""
    # NEW endpoint - this respects sk_ key
    return f"https://gen.pollinations.ai/image/{enc}?model=flux&nologo=true&safe=true{key_part}&seed={random.randint(1,999999)}"
# Show history
for role, content in st.session_state.history:
    with st.chat_message(role):
        if content.startswith("http"):
            st.image(content)
        else:
            st.write(content)

# THIS IS THE MESSAGE BOX - IT WAS MISSING
user_prompt = st.chat_input("Ask anything or say 'picture of a cat'...")

if user_prompt:
    # Save user
    st.session_state.history.append(("user", user_prompt))
    with st.chat_message("user"):
        st.write(user_prompt)

    # Check blocked
    if "picture" in user_prompt.lower() or "image" in user_prompt.lower() or "draw" in user_prompt.lower():
        if is_blocked(user_prompt):
            reply = "❌ Sorry, I cannot generate pictures of real people, children, or political figures for safety. Try 'picture of a lion' or 'sunset over Ghana'."
            st.session_state.history.append(("assistant", reply))
            with st.chat_message("assistant"):
                st.write(reply)
        else:
            url = gen_image_url(user_prompt)
            st.session_state.history.append(("assistant", url))
            with st.chat_message("assistant"):
                st.image(url)
    else:
        answer = ask_any_question(user_prompt)
        st.session_state.history.append(("assistant", answer))
        with st.chat_message("assistant"):
            st.write(answer)
