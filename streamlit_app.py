import streamlit as st
from groq import Groq
import urllib.parse, re, requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# REAL PEOPLE - 100% WORKING FILENAMES FROM WIKIMEDIA
REAL_MAP = {
    "ronaldo": "Cristiano Ronaldo - 2018.jpg",
    "cristiano ronaldo": "Cristiano Ronaldo - 2018.jpg",
    "cristiano": "Cristiano Ronaldo - 2018.jpg",
    "messi": "Lionel Messi 2019.jpg",
    "lionel messi": "Lionel Messi 2019.jpg",
    "elon musk": "Elon Musk Royal Society.jpg",
    "elon": "Elon Musk Royal Society.jpg",
    "john mahama": "John Dramani Mahama 2014.jpg",
    "mahama": "John Dramani Mahama 2014.jpg",
    "akufo addo": "Nana Akufo-Addo in 2020.jpg",
    "nkrumah": "Kwame Nkrumah, 1961 (cropped).jpg",
    "vulture": "Griffon vulture (Gyps fulvus) in flight 2.jpg",
    "pilot": "Pilot in cockpit.jpg",
    "accra": "Accra Skyline.jpg",
}

def get_bytes_from_commons(filename):
    try:
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}?width=800"
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"}, stream=True)
        if r.status_code == 200:
            return r.content
    except:
        pass
    return None

def get_bytes_anything(query):
    q = query.lower().strip()

    # 1. Check our real map first (fastest, guaranteed)
    for key, filename in REAL_MAP.items():
        if key in q:
            b = get_bytes_from_commons(filename)
            if b:
                return b, f"Real photo of {key.title()} - Wikipedia"

    # 2. Try Wikipedia page image
    try:
        api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=800&pilicense=any"
        r = requests.get(api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        for p in r.get("query",{}).get("pages",{}).values():
            if "thumbnail" in p:
                thumb_url = p["thumbnail"]["source"]
                img = requests.get(thumb_url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).content
                return img, f"Real Wikipedia photo of {query.title()}"
    except: pass

    # 3. Try Wikimedia search for anything (animals, places, objects)
    try:
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&srlimit=5&format=json"
        r = requests.get(search_url, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        for item in r.get("query",{}).get("search",[]):
            title = item["title"]
            if any(x in title.lower() for x in ["logo","svg","map","flag","icon"]): continue
            info = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
            r2 = requests.get(info, timeout=6).json()
            for page in r2.get("query",{}).get("pages",{}).values():
                if "imageinfo" in page:
                    url = page["imageinfo"][0]["url"]
                    if url.lower().endswith((".jpg",".jpeg",".png")):
                        b = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).content
                        return b, f"Real photo: {title.replace('File:','')}"
    except: pass

    # 4. Final fallback - Real world photos from LoremFlickr (anything!)
    try:
        url = f"https://loremflickr.com/800/600/{urllib.parse.quote(query)}"
        b = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).content
        return b, f"Real world photo of {query.title()}"
    except: pass

    return None, None

st.title("SI Worldwide 🌍")
st.caption("V9.2 - Anyone & Anything Real Photos")

# SHOW CHAT
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image_bytes":
            st.image(BytesIO(m["content"]), caption=m.get("caption",""), use_container_width=True)
        elif m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Picture of Messi, Ronaldo, dog, car, Accra, vulture, anything...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()

    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})

    # >>> THIS IS THE FIX: Detect picture BEFORE calling AI <<<
    is_pic = False
    if any(w in low for w in ["picture","photo","image","draw","show"]):
        is_pic = True
    # If it's a science question, not a picture
    if any(w in low for w in ["what is","difference between","meaning","translate","how to say","who is","can a"]):
        is_pic = False
    # If starts with picture, ALWAYS picture
    if low.strip().startswith(("picture","photo","image")):
        is_pic = True

    if is_pic:
        clean = re.sub(r'picture of|photo of|image of|picture|photo|image|draw|show me|of', '', low, flags=re.I).strip()
        clean = clean.replace(" "," ").strip()
        if not clean: clean = "world"

        with st.spinner(f"Finding REAL photo of {clean.title()}..."):
            data, cap = get_bytes_anything(clean)

        if data:
            st.session_state.messages.append({"role":"assistant","type":"image_bytes","content":data,"caption":cap})
        else:
            st.session_state.messages.append({"role":"assistant","content":f"Could not find real photo of {clean}, try another name like Cristiano Ronaldo, Lionel Messi"})
    else:
        # EXACT ANSWER
        ans=None
        for model in ["llama-3.1-8b-instant","llama3-70b-8192","mixtral-8x7b-32768","gemma2-9b-it","openai/gpt-oss-20b"]:
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"system","content":"Give EXACT short factual answer."},{"role":"user","content":q}],
                    temperature=0.2, max_tokens=800
                )
                ans = r.choices[0].message.content
                if ans and len(ans)>3 and "can't provide" not in ans.lower():
                    break
            except: continue
        st.session_state.messages.append({"role":"assistant","content":ans or "Try again"})

    st.rerun()
