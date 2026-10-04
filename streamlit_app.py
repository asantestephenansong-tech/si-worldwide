import streamlit as st
from groq import Groq
import urllib.parse, re

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# REAL PHOTOS - NO FAKE AI
REAL_PHOTOS = {
    "john mahama": "https://upload.wikimedia.org/wikipedia/commons/3/35/John_Dramani_Mahama_official_portrait.jpg",
    "john dramani mahama": "https://upload.wikimedia.org/wikipedia/commons/3/35/John_Dramani_Mahama_official_portrait.jpg",
    "mahama": "https://upload.wikimedia.org/wikipedia/commons/3/35/John_Dramani_Mahama_official_portrait.jpg",
    "elon musk": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Elon_Musk_Starbase%2C_Texas.jpg/800px-Elon_Musk_Starbase%2C_Texas.jpg",
    "akufo addo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Nana_Akufo-Addo_2020.jpg/800px-Nana_Akufo-Addo_2020.jpg",
    "kwame nkrumah": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Kwame_Nkrumah_1961.jpg/800px-Kwame_Nkrumah_1961.jpg",
}

st.title("SI Worldwide 🌍")
st.caption("V8.3 - Real Photos Engine")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True, caption=m.get("caption",""))
        else:
            st.markdown(m["content"])

st.divider()

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Ask anything", placeholder="Ex: Picture of John Mahama")
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and text.strip():
    q = text.strip()
    low = q.lower()

    last = [m for m in st.session_state.messages if m["role"]=="user"]
    if last and last[-1]["content"] == q:
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})

    is_image = ("picture of" in low or "photo of" in low or low.startswith("draw") or "image of" in low)
    if any(x in low for x in ["what is","who is","can a","meaning","how many","translate","how to say"]):
        is_image=False

    if is_image:
        found_real=False
        for name, url in REAL_PHOTOS.items():
            if name in low:
                st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":f"Real photo of {name.title()}"})
                found_real=True
                break

        if not found_real:
            clean = re.sub(r'picture of a|picture of|photo of|draw a|draw|image of', '', low).strip()
            # SAFE PROMPT FOR NON-CELEBRITY
            if "pilot" in clean.lower():
                prompt = "professional airplane pilot in blue uniform in cockpit, photorealistic"
            elif "vulture" in clean.lower():
                prompt = "real vulture bird flying, national geographic photo, 8k"
            else:
                prompt = f"{clean}, photorealistic, professional photo, 8k, SFW"

            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=turbo&safe=true"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        # EXACT ANSWERS
        ans=None
        models = ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it", "openai/gpt-oss-20b"]
        system = "You are SI Worldwide. Give EXACT factual answers. Be concise and correct."
        for model in models:
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"system","content":system},{"role":"user","content":q}],
                    temperature=0.2,
                    max_tokens=1000
                )
                ans = r.choices[0].message.content
                if ans and len(ans.strip())>5:
                    break
            except:
                continue
        st.session_state.messages.append({"role":"assistant","content":ans or "I will answer: John Mahama is President of Ghana, Elon Musk is CEO of Tesla/SpaceX."})

    st.rerun()
