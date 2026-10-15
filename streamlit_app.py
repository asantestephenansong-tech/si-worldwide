import streamlit as st
from groq import Groq
import requests
from gtts import gTTS

st.set_page_config(page_title="SI Worldwide V8.2", page_icon="🌍", layout="wide")

GROQ_KEY = st.secrets["GROQ_API_KEY"]
HF_KEY = st.secrets.get("HF_API_KEY", "")
client = Groq(api_key=GROQ_KEY)

if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.title("🌍 SI V8.2")
    st.divider()
    st.subheader("📜 History")
    if not st.session_state.history:
        st.caption("No images yet")
    else:
        for item in reversed(st.session_state.history[-10:]):
            st.image(item['image'], use_container_width=True)
            st.caption(item['prompt'][:50])
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

st.title("Intelligence Worldwide V8.2")
st.caption("Samson Fixed ✅ | Jersey Fixed ✅ | Voice + History ✅")

prompt = st.text_input("What do you want to create?", placeholder="e.g. Samson with long hair, or Messi in Argentina jersey")

def enhance_prompt(user_prompt):
    # SAFE ENHANCER - never crashes
    try:
        system = """You are SI Prompt Enhancer. RULES: If SAMSON add 'long hair, ancient Israelite, muscular'. If DAVID add 'young shepherd, sling'. If FOOTBALL add correct jersey. Add 'ultra detailed, 8k'. Return ONLY prompt."""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # NEW WORKING MODEL
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # If Groq fails, use smart local fix
        print(f"Groq error: {e}")
        enhanced = user_prompt
        if "samson" in user_prompt.lower():
            enhanced += ", long hair, ancient Israelite, muscular, biblical"
        if "david" in user_prompt.lower() and "goliath" in user_prompt.lower():
            enhanced += ", young shepherd boy with sling"
        return enhanced + ", ultra detailed, 8k, cinematic"

if st.button("✨ Generate Image", type="primary", use_container_width=True) and prompt:
    with st.spinner("SI is creating..."):
        enhanced = enhance_prompt(prompt)
        st.write(f"**Enhanced:** {enhanced}")

        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_KEY}"}
        r = requests.post(API_URL, headers=headers, json={"inputs": enhanced})

        if r.status_code == 200:
            with open("output.png", "wb") as f:
                f.write(r.content)
            st.image("output.png")
            st.session_state.history.append({"prompt": prompt, "image": "output.png"})
            try:
                tts = gTTS(f"Created {prompt[:30]}", lang='en')
                tts.save("voice.mp3")
                st.audio("voice.mp3")
            except:
                pass
            st.success("Done!")
        else:
            st.error(f"Image Error: {r.text[:200]}")

st.divider()
st.markdown("**SI Worldwide V8.2 | Always There | Ghana 🇬🇭**")
