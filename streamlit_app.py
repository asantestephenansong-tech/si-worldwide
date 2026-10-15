import streamlit as st
from groq import Groq
import requests
import time
from gtts import gTTS
import os
import replicate

# --- PAGE CONFIG ---
st.set_page_config(page_title="SI Worldwide V8.0", page_icon="🌍", layout="wide")

# --- API KEYS (from secrets) ---
GROQ_KEY = st.secrets["GROQ_API_KEY"]
HF_KEY = st.secrets.get("HF_API_KEY", "")
REPLICATE_KEY = st.secrets.get("REPLICATE_API_TOKEN", "")

client = Groq(api_key=GROQ_KEY)

# --- HISTORY MEMORY ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_image' not in st.session_state:
    st.session_state.last_image = None

# --- SIDEBAR - HISTORY ---
with st.sidebar:
    st.title("🌍 SI Worldwide V8.0")
    st.markdown("**Always There - Super Powers**")
    st.divider()
    st.subheader("📜 History")
    if not st.session_state.history:
        st.caption("No images yet")
    else:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            st.image(item['image'], use_container_width=True)
            st.caption(f"{item['prompt'][:60]}...")
            st.divider()

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("Uptime: 100% - Always There ✅")
    st.caption("https://si-worldwide.streamlit.app")

# --- MAIN ---
st.title("🌍 Stephen's Intelligence Worldwide V8.0")
st.caption("Samson Fixed ✅ | Football Jersey Fixed ✅ | Voice + History + Video")

# --- VOICE INPUT ---
col1, col2 = st.columns([3,1])
with col1:
    prompt = st.text_input("What do you want to create?", placeholder="e.g. Samson with long hair fighting lion, or Ronaldo in Portugal jersey")
with col2:
    st.write("")
    st.write("")
    voice_prompt = st.button("🎤 Talk")

# --- V8.0 BIBLE & JERSEY FIX ENGINE (FROM V7.0) ---
def enhance_prompt(user_prompt):
    system = """
    You are SI Prompt Enhancer V8.0.
    RULES:
    1. If prompt mentions SAMSON: ALWAYS add "long hair, ancient Israelite, muscular, biblical"
    2. If prompt mentions DAVID: ALWAYS add "young shepherd boy, no armor, sling"
    3. If prompt mentions FOOTBALL PLAYER + JERSEY: ALWAYS use correct country/club jersey. e.g. "Ronaldo Portugal jersey" -> "Cristiano Ronaldo wearing Portugal national team jersey red green"
    4. Add "ultra detailed, 8k, cinematic"
    Return ONLY enhanced prompt.
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

# --- GENERATE ---
if st.button("✨ Generate Image", type="primary", use_container_width=True) and prompt:
    with st.spinner("SI is creating..."):
        enhanced = enhance_prompt(prompt)
        st.write(f"**Enhanced:** {enhanced}")

        # HuggingFace FLUX (your current engine)
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_KEY}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": enhanced})

        if response.status_code == 200:
            # Save image
            with open("output.png", "wb") as f:
                f.write(response.content)

            st.image("output.png", caption=enhanced)
            st.session_state.last_image = "output.png"

            # Add to history
            st.session_state.history.append({"prompt": prompt, "image": "output.png", "enhanced": enhanced})

            # Voice output
            tts = gTTS(f"Created: {prompt}", lang='en')
            tts.save("voice.mp3")
            st.audio("voice.mp3")
            st.success("Image created + Voice + Saved to History!")
        else:
            st.error(f"Error: {response.text}")

# --- V8.0 NEW: VIDEO BUTTON ---
if st.session_state.last_image:
    st.divider()
    st.subheader("🎬 Super Power: Make Video")
    if st.button("Animate Last Image to 5s Video"):
        if not REPLICATE_KEY:
