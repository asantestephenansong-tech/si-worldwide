import streamlit as st
import requests
from groq import Groq
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SI Worldwide AI V14",
    page_icon="🌍",
    layout="centered"
)

# --- GROQ CLIENT ---
# Make sure GROQ_API_KEY is in Streamlit Secrets
client = Groq(api_key=st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ"))

# --- FIXED MODEL (OLD ONE WAS DELETED) ---
GROQ_MODEL = "llama-3.1-8b-instant"  # or "llama-3.3-70b-versatile"

# --- SAFETY - Only block harmful, not pictures or public figures ---
BLOCKED_WORDS = [
    "child porn", "nude child", "sex with child",
    "school girl nude", "school boy nude"
]

def is_blocked(prompt: str) -> bool:
    p = prompt.lower()
    return any(w in p for w in BLOCKED_WORDS)

# --- SYSTEM PROMPT - FIXED ---
SYSTEM_PROMPT = f"""You are SI Worldwide AI V14 built by Stephen Asante.
Today is {datetime.now().strftime('%B %Y')}.
Current facts you MUST use:
- Pope is Leo XIV (since May 8, 2025), not Francis
- US President is Donald Trump (since Jan 20, 2025)
- Ghana President is John Mahama (since Jan 7, 2025)
- Ghana Vice President is Jane Naana Opoku-Agyemang

Rules:
1. Never say you are Pollinations, Pollen, OpenAI, or Meta.
2. You are SI Worldwide AI V14 - Answers ANY question you throw at me - No timeout.
3. If user asks for picture of a PRIVATE child, refuse for safety.
4. For public figures like Elon Musk, Messi, Shatta Wale, Donald Trump, John Mahama - you CAN generate as AI illustration. Say: 'This is an AI illustration, not a real photo.'
5. Keep answers short, helpful, friendly. Use same language as user.
6. Today in Ghana is {datetime.now().strftime('%A, %B %d, %Y')}.
"""

# --- UI ---
st.title("🌍 SI Worldwide AI V14")
st.caption("Answers ANY question you throw at me - No timeout")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask anything... picture of elon musk, etc"):

    # Safety check
    if is_blocked(prompt):
        with st.chat_message("assistant"):
            st.error("I can't generate that content for safety reasons. Try a public figure or educational topic.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if user wants picture
    is_image_request = any(k in prompt.lower() for k in ["picture of", "image of", "generate image", "photo of", "draw"])

    with st.chat_message("assistant"):
        if is_image_request:
            # Use Pollinations for images (free, no key needed)
            # Clean prompt
            safe_prompt = prompt.replace("picture of", "").replace("image of", "").strip()
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(safe_prompt)}?width=1024&height=1024&nologo=true&model=flux"
            st.image(image_url, caption=f"AI illustration: {safe_prompt}")
            st.caption("This is an AI illustration, not a real photo.")
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_url})
        else:
            # Text answer via Groq
            try:
                completion = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                answer = completion.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": answer})
            except Exception as e:
                st.error(f"Groq error: {e}. Check your API key and model name.")
