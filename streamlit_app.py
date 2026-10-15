import streamlit as st
from groq import Groq
import requests
from gtts import gTTS

# --- PAGE CONFIG ---
st.set_page_config(page_title="SI Worldwide V8.1", page_icon="🌍", layout="wide")

# --- API KEYS ---
GROQ_KEY = st.secrets["GROQ_API_KEY"]
HF_KEY = st.secrets.get("HF_API_KEY", "")

client = Groq(api_key=GROQ_KEY)

# --- HISTORY MEMORY ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR - HISTORY ---
with st.sidebar:
    st.title("🌍 SI Worldwide V8.1")
    st.markdown("**Always There**")
    st.divider()
    st.subheader("📜 History")
    if not st.session_state.history:
        st.caption("No images yet")
    else:
        for item in reversed(st.session_state.history[-10:]):
            st.image(item['image'], use_container_width=True)
            st.caption(item['prompt'][:60])
            st.divider()
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
    st.caption("Uptime: 100% ✅")

# --- MAIN ---
st.title("🌍 Stephen's Intelligence Worldwide V8.1")
st.caption("Samson Fixed ✅ | Jersey Fixed ✅ | Voice + History ✅")

prompt = st.text_input("What do you want to create?", placeholder="e.g. Samson with long hair fighting lion")

# --- V7 FIX ENGINE ---
def enhance_prompt(user_prompt):
    system = """You are SI Prompt Enhancer.
    RULES:
    1. If SAMSON: add 'long hair, ancient Israelite, muscular, biblical'
    2. If DAVID: add 'young shepherd boy, sling, no armor'
    3. If FOOTBALL + JERSEY: use correct country jersey.
    4. Add 'ultra detailed, 8k, cinematic'. Return ONLY enhanced prompt."""
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

        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_KEY}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": enhanced})

        if response.status_code == 200:
            with open("output.png", "wb") as f:
                f.write(response.content)

            st.image("output.png", caption=enhanced)

            # History
            st.session_state.history.append({"prompt": prompt, "image": "output.png"})

            # Voice
            try:
                tts = gTTS(f"Created {prompt}", lang='en')
                tts.save("voice.mp3")
                st.audio("voice.mp3")
            except:
                pass

            st.success("Created + Saved to History!")
        else:
            st.error(f"Error: {response.text}")

st.divider()
st.markdown("**SI Worldwide V8.1 | Always There | Ghana 🇬🇭**")
