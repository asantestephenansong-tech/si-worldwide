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
client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# --- SAFETY - Only block harmful ---
BLOCKED_WORDS = [
    "child porn", "nude child", "sex with child",
    "school girl nude", "school boy nude"
]

def is_blocked(prompt: str) -> bool:
    p = prompt.lower()
    return any(w in p for w in BLOCKED_WORDS)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""You are SI Worldwide AI V14 built by Stephen Asante.
Today is {datetime.now().strftime('%B %Y')}.
Current facts you MUST use:
- Pope is Leo XIV (since May 8, 2025), not Francis
- US President is Donald Trump (since Jan 20, 2025)
- Ghana President is John Mahama (since Jan 7, 2025)
- Vice President is Jane Naana Opoku-Agyemang
- You are SI Worldwide AI V14 - Answers ANY question - No timeout
- Never say you are Pollinations, Pollen, OpenAI, Meta.
- For public figures like Elon Musk, Messi, Shatta Wale, Trump, Mahama you CAN generate image as AI illustration, say 'This is an AI illustration, not a real photo.'
- If user asks for private child sexual content, refuse.
- Keep answers short, helpful, friendly. Use same language as user.
"""

# --- UI ---
st.title("🌍 SI Worldwide AI V14")
st.caption("Answers ANY question you throw at me - No timeout")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
            st.image(msg["content"])
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything... picture of elon musk, etc"):

    if is_blocked(prompt):
        with st.chat_message("assistant"):
            st.error("I can't generate that content for safety reasons.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    is_image_request = any(k in prompt.lower() for k in ["picture of", "image of", "generate image", "photo of", "draw", "picture"])

    with st.chat_message("assistant"):
        if is_image_request:
            safe_prompt = prompt.lower().replace("picture of", "").replace("image of", "").replace("generate image of", "").replace("photo of", "").replace("draw", "").strip()
            if not safe_prompt:
                safe_prompt = prompt
            # Pollinations - Flux model
            encoded = requests.utils.quote(safe_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux&seed={datetime.now().microsecond}"
            st.image(image_url, caption=f"AI illustration: {safe_prompt}")
            st.caption("This is an AI illustration, not a real photo.")
            st.session_state.messages.append({"role": "assistant", "type": "image", "content": image_url})
        else:
            # AUTO FALLBACK FOR GROQ - NEVER SHOWS 404 AGAIN
            MODELS_TO_TRY = [
                "llama-3.3-70b-versatile",
                "gemma2-9b-it",
                "openai/gpt-oss-20b",
                "llama-3.1-8b-instant"
            ]
            answer = None
            last_error = ""
            for model_name in MODELS_TO_TRY:
                try:
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    answer = completion.choices[0].message.content
                    break
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": answer})
            else:
                st.error(f"All models failed. Last error: {last_error}. Check your GROQ_API_KEY in Streamlit Secrets.")
