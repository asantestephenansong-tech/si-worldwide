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

PEOPLE = {
    "ronaldo": "Cristiano Ronaldo.jpg",
    "cristiano ronaldo": "Cristiano Ronaldo.jpg",
    "cristiano": "Cristiano Ronaldo.jpg",
    "messi": "Lionel Messi 20180626.jpg",
    "lionel messi": "Lionel Messi 20180626.jpg",
    "elon musk": "Elon Musk Royal Society.jpg",
    "elon": "Elon Musk Royal Society.jpg",
    "mahama": "John Dramani Mahama 2014.jpg",
    "nkrumah": "Kwame Nkrumah, 1961 (cropped).jpg",
}

def get_image(query):
    q = query.lower().strip()
    safe_q = q.replace("girls","young women").replace("girl","young woman")

    if any(x in q for x in ["nude","naked","sex","porn"]):
        return None, "Cannot provide nude images."

    # PEOPLE - Wikipedia API first (never breaks like your Messi now!)
    for name in PEOPLE.keys():
        if name in q:
            try:
                api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(name.title())}&prop=pageimages&format=json&pithumbsize=800"
                r = requests.get(api, timeout=5, headers={"User-Agent":"Mozilla/5.0"}).json()
                for p in r.get("query",{}).get("pages",{}).values():
                    if "thumbnail" in p:
                        return p["thumbnail"]["source"], f"Real photo of {name.title()} - Wikipedia"
            except: pass
            url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(PEOPLE[name])}?width=800"
            return url, f"Real photo of {name.title()} - Wikimedia"

    # Non-people try Wikipedia too
    try:
        api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=800"
        r = requests.get(api, timeout=5, headers={"User-Agent":"Mozilla/5.0"}).json()
        for p in r.get("query",{}).get("pages",{}).values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], f"Real Wikipedia photo of {query.title()}"
    except: pass

    if "fight" in safe_q:
        prompt = f"real photograph of {safe_q} as sports boxing competition, wearing full sports uniform and gloves, fully clothed, safe"
    else:
        prompt = f"real photograph of {safe_q}, fully clothed, modest clothing, professional photo"

    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=800&height=600&nologo=true&model=turbo&safe=true&seed={abs(hash(safe_q))%10000}"
    return url, f"Photo of {query.title()} (safe)"

st.title("SI Worldwide 🌍")
st.caption("V9.8 - Final Worldwide Stable - Messi Working!")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()
with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Ask anything...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()
    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})

    is_pic = any(w in low for w in ["picture","photo","image","draw","show"])
    if any(w in low for w in ["what is","difference","meaning","translate","who was","who is"]):
        is_pic=False
    if low.strip().startswith(("picture","photo","image")):
        is_pic=True

    if is_pic:
        clean = re.sub(r'picture of a|picture of|photo of|image of|picture|photo|image|draw|show me', '', low, flags=re.I).strip()
        if not clean: clean="messi"
        url, cap = get_image(clean)
        if url is None:
            st.session_state.messages.append({"role":"assistant","content":cap})
        else:
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
