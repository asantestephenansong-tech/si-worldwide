import streamlit as st
from groq import Groq
import urllib.parse, re, requests

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ONLY REAL PEOPLE HERE - 100% ACCURATE REAL WIKIPEDIA PHOTOS
PEOPLE_PHOTOS = {
    "ronaldo": "https://commons.wikimedia.org/wiki/Special:FilePath/Cristiano%20Ronaldo%20-%202018.jpg?width=800",
    "cristiano ronaldo": "https://commons.wikimedia.org/wiki/Special:FilePath/Cristiano%20Ronaldo%20-%202018.jpg?width=800",
    "messi": "https://commons.wikimedia.org/wiki/Special:FilePath/Lionel%20Messi%202019.jpg?width=800",
    "lionel messi": "https://commons.wikimedia.org/wiki/Special:FilePath/Lionel%20Messi%202019.jpg?width=800",
    "elon musk": "https://commons.wikimedia.org/wiki/Special:FilePath/Elon%20Musk%20Royal%20Society.jpg?width=800",
    "john mahama": "https://commons.wikimedia.org/wiki/Special:FilePath/John%20Dramani%20Mahama%202014.jpg?width=800",
    "mahama": "https://commons.wikimedia.org/wiki/Special:FilePath/John%20Dramani%20Mahama%202014.jpg?width=800",
    "akufo addo": "https://commons.wikimedia.org/wiki/Special:FilePath/Nana%20Akufo-Addo%20in%202020.jpg?width=800",
    "nkrumah": "https://commons.wikimedia.org/wiki/Special:FilePath/Kwame%20Nkrumah%2C%201961%20%28cropped%29.jpg?width=800",
}

def get_photo(query):
    low = query.lower().strip()

    # 1. Check if it's a PERSON - give REAL Wikipedia photo
    for name, url in PEOPLE_PHOTOS.items():
        if name in low:
            return url, f"Real photo of {name.title()} - Wikipedia"

    # 2. For EVERYTHING ELSE (goat, car, dog, house, vulture, pilot)
    # Use Pollinations TURBO which is VERY accurate for animals/things
    # NOT Wikimedia search (that gave you airport for goat!)
    clean_prompt = f"real high quality professional photograph of {query}, 8k, photorealistic, accurate, no cartoon"
    # Use seed to make it real
    poll_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=800&height=600&nologo=true&model=turbo&safe=true&seed={hash(query) % 1000}"
    return poll_url, f"Realistic photo of {query.title()}"

st.title("SI Worldwide 🌍")
st.caption("V9.4 - Real People + Real Things Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            try:
                st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
            except:
                st.markdown(f"[Open Image]({m['content']})")
        else:
            st.markdown(m["content"])

st.divider()

with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Picture of a goat, ronaldo, car, dog...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()

    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})

    is_pic = False
    if any(w in low for w in ["picture","photo","image","draw","show"]):
        is_pic = True
    if any(w in low for w in ["what is","difference between","meaning","translate","how to say","who was","can a","who is"]):
        is_pic = False
    if low.strip().startswith(("picture","photo","image")):
        is_pic = True

    if is_pic:
        clean = re.sub(r'picture of a|picture of|photo of|image of|picture|photo|image|draw|show me', '', low, flags=re.I).strip()
        clean = clean.replace(" a "," ").strip()
        if not clean or len(clean)<2:
            clean = "goat" if "goat" in low else "car"

        url, cap = get_photo(clean)
        st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":cap})
    else:
        ans=None
        for model in ["llama-3.1-8b-instant","llama3-70b-8192","mixtral-8x7b-32768","gemma2-9b-it","openai/gpt-oss-20b"]:
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"system","content":"Give EXACT short factual answer."},{"role":"user","content":q}],
                    temperature=0.2, max_tokens=800
                )
                ans = r.choices[0].message.content
                if ans and len(ans)>3:
                    break
            except: continue
        st.session_state.messages.append({"role":"assistant","content":ans or "Try again"})

    st.rerun()
