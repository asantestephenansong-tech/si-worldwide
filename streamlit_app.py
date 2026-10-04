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

# REAL WIKIPEDIA PHOTOS - Works 100%
PEOPLE = {
    "elon musk": "Elon Musk Royal Society.jpg",
    "elon": "Elon Musk Royal Society.jpg",
    "ronaldo": "Cristiano Ronaldo - 2018.jpg",
    "cristiano": "Cristiano Ronaldo - 2018.jpg",
    "messi": "Lionel Messi 2019.jpg",
    "lionel messi": "Lionel Messi 2019.jpg",
    "mahama": "John Dramani Mahama 2014.jpg",
    "john mahama": "John Dramani Mahama 2014.jpg",
    "akufo addo": "Nana Akufo-Addo in 2020.jpg",
    "nkrumah": "Kwame Nkrumah, 1961 (cropped).jpg",
    "obama": "Barack Obama.jpg",
    "trump": "Donald Trump official portrait.jpg",
    "beyonce": "Beyonce - 2019.jpg",
    "shatta wale": "Shatta Wale.jpg",
    "stonebwoy": "Stonebwoy - 2019.jpg",
}

def get_image_url(query):
    q = query.lower().strip()

    # 1. PEOPLE - Real Wikipedia
    for name, filename in PEOPLE.items():
        if name in q:
            url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}?width=800"
            return url, f"Real photo of {name.title()} - Wikimedia"

    # 2. Try Wikipedia thumbnail for any other person/thing (goat, car, Accra)
    try:
        api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=800&pilicense=any"
        r = requests.get(api, timeout=5, headers={"User-Agent":"Mozilla/5.0"}).json()
        for p in r.get("query",{}).get("pages",{}).values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], f"Real Wikipedia photo of {query.title()}"
    except: pass

    # 3. EVERYTHING ELSE - Realistic accurate photo (goat, car, dog, vulture, pilot)
    # Use prompt that forces real animal, not airport!
    prompt = f"a real photograph of {query}, professional photo, 8k, photorealistic, accurate"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=800&height=600&nologo=true&model=turbo&seed={abs(hash(query))%10000}"
    return url, f"Photo of {query.title()}"

st.title("SI Worldwide 🌍")
st.caption("V9.5 - Real Worldwide Final")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()
with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Picture of a goat, Ronaldo, Messi, car...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()
    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})

    is_pic = any(w in low for w in ["picture","photo","image","draw","show"])
    if any(w in low for w in ["what is","difference","meaning","translate","who was","who is","how to","can a"]):
        is_pic=False
    if low.strip().startswith(("picture","photo","image")):
        is_pic=True

    if is_pic:
        clean = re.sub(r'picture of a|picture of|photo of|image of|picture|photo|image|draw|show me', '', low, flags=re.I).strip()
        if not clean: clean="goat"
        url, cap = get_image_url(clean)
        st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":cap})
    else:
        ans=None
        for model in ["llama-3.1-8b-instant","llama3-70b-8192","mixtral-8x7b-32768","gemma2-9b-it","openai/gpt-oss-20b"]:
            try:
                r = client.chat.completions.create(model=model, messages=[{"role":"system","content":"Give EXACT short answer."},{"role":"user","content":q}], temperature=0.2, max_tokens=800)
                ans = r.choices[0].message.content
                if ans and len(ans)>3: break
            except: continue
        st.session_state.messages.append({"role":"assistant","content":ans or "Try again"})
    st.rerun()
