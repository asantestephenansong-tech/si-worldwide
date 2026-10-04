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

def get_anyone_photo(query):
    q = query.strip()
    low = q.lower()
    safe_q = low.replace("girls","young women")

    if any(x in low for x in ["nude","naked","sex","porn"]):
        return None, "Cannot provide nude images."

    # UNIVERSAL SEARCH - Works for ANYONE (mbape, vulture, Mahama)
    try:
        search_api = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json&srlimit=1"
        r = requests.get(search_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        results = r.get("query",{}).get("search",[])
        if results:
            title = results[0]["title"]
            thumb_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=800"
            r2 = requests.get(thumb_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
            for p in r2.get("query",{}).get("pages",{}).values():
                if "thumbnail" in p:
                    return p["thumbnail"]["source"], f"Real photo of {title} - Wikipedia"
    except: pass

    try:
        thumb_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(q)}&prop=pageimages&format=json&pithumbsize=800"
        r = requests.get(thumb_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        for p in r.get("query",{}).get("pages",{}).values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], f"Real Wikipedia photo of {q.title()}"
    except: pass

    prompt = f"real photograph of {safe_q}, fully clothed, professional, 8k, accurate"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=800&height=600&nologo=true&model=turbo&safe=true&seed={abs(hash(safe_q))%9999}"
    return url, f"Photo of {q.title()}"

def answer_any(question):
    models = ["llama-3.3-70b-versatile","llama-3.1-8b-instant","openai/gpt-oss-120b","gemma2-9b-it"]
    system = """You are SI Worldwide. Current date: May 2026.
CRITICAL FACTS (2026):
- Kylian Mbappe plays for Real Madrid since July 2024 (not PSG)
- Lionel Messi plays for Inter Miami
- Cristiano Ronaldo plays for Al-Nassr
- John Mahama is President of Ghana (since Jan 2025)
- Always give current 2026 info, not old.
Answer short, exact, current."""
    for model in models:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":system},{"role":"user","content":question}],
                temperature=0.2, max_tokens=1000
            )
            ans = r.choices[0].message.content
            if ans and len(ans)>10:
                return ans
        except: continue
    return "Please ask again with more detail."

st.title("SI Worldwide 🌍")
st.caption("V10.1 - Mbappe Real + 2026 Answers")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()
with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Picture of anyone, any question...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()
    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})

    is_pic = any(w in low for w in ["picture","photo","image","draw","show"])
    if any(w in low for w in ["which","what is","who","how","when","where","why","can a","difference","meaning"]):
        if not low.strip().startswith(("picture","photo","image")):
            is_pic=False
    if low.strip().startswith(("picture","photo","image")):
        is_pic=True

    if is_pic:
        clean = re.sub(r'picture of a|picture of|photo of|image of|picture|photo|image|draw|show me', '', low, flags=re.I).strip()
        if not clean: clean=q
        if "mbape" in clean: clean="Kylian Mbappe"
        url, cap = get_anyone_photo(clean)
        st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":cap})
    else:
        ans = answer_any(q)
        st.session_state.messages.append({"role":"assistant","content":ans})
    st.rerun()
