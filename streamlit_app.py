import streamlit as st
import requests
from groq import Groq
import random, time
from urllib.parse import quote

# SAFETY FILTER - to avoid ban
BLOCKED_WORDS = ["school girl", "school boy", "messi", "mahama", "ronaldo", "trump", "biden", "nude", "sex", "fight", "child"]
def is_blocked(prompt):
    return any(w in prompt.lower() for w in BLOCKED_WORDS)

# CURRENT INFO - fix old answers
SYSTEM_PROMPT = """You are SI V14. Today is 2026.
Current facts you MUST use:
- Pope is Leo XIV (since May 2025), not Francis
- US President is Donald Trump (since Jan 2025)
- Ghana President is John Mahama (since Jan 2025)
Never say you are Pollinations or Pollen.
If user asks for picture of real person or child, say: 'Sorry, I cannot generate pictures of real people or children for safety.'
"""

st.set_page_config(page_title="SI Worldwide")
st.title("🌍 SI Worldwide AI")
st.caption("V14 - Answers ANY question you throw")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_KEY = st.secrets.get("HF_API_KEY", "")
POLLEN_KEY = st.secrets.get("POLLEN_API_KEY", "")  # <-- YOU WERE MISSING THIS

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.last_image_time = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def ask_any_question(prompt):
    # 1. Groq - 3 models rotation
    if client:
        for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.1-70b-versatile"]:
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
    
    # 2. Pollinations text with KEY
    try:
        headers = {"Authorization": f"Bearer {POLLEN_KEY}", "Content-Type": "application/json"} if POLLEN_KEY else {}
        r = requests.post(
            "https://text.pollinations.ai/openai",
            headers=headers,
            json={
                "model": "openai",
                "messages": [{"role": "user", "content": prompt}],
                "system": SYSTEM_PROMPT
            },
            timeout=30
        )
        if r.ok:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    
    return "Free limit reached? Add POLLEN_API_KEY with sk_... in Secrets and Reboot."

# YOUR IMAGE FUNCTION - fix it to use key
def gen_image(prompt):
    if is_blocked(prompt):
        return None, "❌ Sorry, I cannot generate real people, children. Try 'vulture', 'landscape', 'cat'."
    
    encoded = quote(prompt)
    # Use key if exists
    key_param = f"&key={POLLEN_KEY}" if POLLEN_KEY else ""
    url = f"https://image.pollinations.ai/prompt/{encoded}?nologo=true&safe=true{key_param}&seed={random.randint(1,999999)}"
    return url, None
