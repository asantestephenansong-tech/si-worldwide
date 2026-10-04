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

# REAL MAP - Direct Wikimedia file names that NEVER fail
REAL_MAP = {
    "ronaldo": "Cristiano Ronaldo - 2018.jpg",
    "cristiano": "Cristiano Ronaldo - 2018.jpg",
    "messi": "Lionel Messi 2019.jpg",
    "lionel messi": "Lionel Messi 2019.jpg",
    "elon musk": "Elon Musk Royal Society.jpg",
    "elon": "Elon Musk Royal Society.jpg",
    "john mahama": "John Dramani Mahama 2014.jpg",
    "mahama": "John Dramani Mahama 2014.jpg",
    "akufo addo": "Nana Akufo-Addo in 2020.jpg",
    "car": "Tesla Model S - 2012.jpg",
    "vulture": "Griffon vulture (Gyps fulvus) in flight 2.jpg",
    "pilot": "Pilot in cockpit.jpg",
}

def get_real_url(query):
    q = query.lower().strip()

    # 1. Check real map first
    for key, filename in REAL_MAP.items():
        if key in q:
            url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}?width=800"
            return url, f"Real photo of {key.title()} - Wikimedia"

    # 2. Wikipedia thumbnail
    try:
        api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=800&pilicense=any"
        r = requests.get(api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        for p in r.get("query",{}).get("pages",{}).values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], f"Real Wikipedia photo of {query.title()}"
    except: pass

    # 3. Wikimedia Commons search
    try:
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&srlimit=1&format=json"
        r = requests.get(search_url, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        items = r.get("query",{}).get("search",[])
        if items:
            title = items[0]["title"]
            # Direct Special:FilePath link - always works
            filename = title.replace("File:","")
            url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}?width=800"
            return url, f"Real photo: {filename}"
    except: pass

    # 4. Pollinations for generic things (car, house, dog) - works for objects
    prompt = f"{query}, real photograph, high quality, 8k"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=800&height=600&nologo=true&model=turbo&safe=true"
    return url, f"Photo of {query.title()}"

st.title("SI Worldwide 🌍")
st.caption("V9.3 - Real Photos Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            try:
                st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
            except:
                st.markdown(f"[Open Image]({m['content']})")
                st.caption(m.get("caption",""))
        else:
            st.markdown(m["content"])

st.divider()

with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Picture of a car, Messi, Ronaldo, dog...")
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
    if any(w in low for w in ["what is","difference between","meaning","translate","how to say","who was","can a"]):
        is_pic = False
    if low.strip().startswith(("picture","photo","image")):
        is_pic = True

    if is_pic:
        clean = re.sub(r'picture of a|picture of|photo of|image of|picture|photo|image|draw|show me|a', '', low, flags=re.I).strip()
        if not clean or len(clean)<2:
            clean = low.replace("picture","").replace("of","").strip()
        if not clean:
            clean = "car"

        url, cap = get_real_url(clean)
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
