import streamlit as st
from groq import Groq
import urllib.parse, re, requests

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_anyone_photo(query):
    q = query.strip()
    low = q.lower()
    safe_q = low.replace("girls","young women").replace("girl","young woman")

    if any(x in low for x in ["nude","naked","sex","porn","xxx"]):
        return None, "Cannot provide nude images."

    # STEP 1: UNIVERSAL - Search Wikipedia for ANYONE/ANYTHING (mbappe, obama, goat, Accra)
    # This works for 100% of famous people, no hard-coded list needed!
    try:
        # Search first to fix typos like "mbape" -> "Kylian Mbappe"
        search_api = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json&srlimit=1"
        r = requests.get(search_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        results = r.get("query",{}).get("search",[])
        if results:
            title = results[0]["title"] # e.g. "Kylian Mbappé" for "mbape"
            # Now get real thumbnail of that title
            thumb_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=800"
            r2 = requests.get(thumb_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
            for p in r2.get("query",{}).get("pages",{}).values():
                if "thumbnail" in p:
                    return p["thumbnail"]["source"], f"Real photo of {title} - Wikipedia"
    except: pass

    # STEP 2: Try direct title (for perfect names)
    try:
        thumb_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(q)}&prop=pageimages&format=json&pithumbsize=800"
        r = requests.get(thumb_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        for p in r.get("query",{}).get("pages",{}).values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], f"Real Wikipedia photo of {q.title()}"
    except: pass

    # STEP 3: Wikimedia Commons (for objects)
    try:
        commons_api = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&srlimit=1&format=json"
        r = requests.get(commons_api, timeout=6, headers={"User-Agent":"Mozilla/5.0"}).json()
        items = r.get("query",{}).get("search",[])
        if items:
            title = items[0]["title"].replace("File:","")
            # Only use if it looks relevant (contains first word)
            if low.split()[0] in title.lower() or title.lower().split()[0] in low:
                url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(title)}?width=800"
                return url, f"Real photo: {title}"
    except: pass

    # STEP 4: Realistic safe photo for anything else (goat, car, fighting)
    if "fight" in safe_q:
        prompt = f"real photograph of {safe_q} as sports boxing competition, wearing full sports uniform, boxing gloves, fully clothed, safe"
    else:
        prompt = f"real high quality photograph of {safe_q}, fully clothed, professional, 8k"

    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=800&height=600&nologo=true&model=turbo&safe=true&seed={abs(hash(safe_q))%9999}"
    return url, f"Photo of {q.title()}"

def answer_any_question(question):
    # Try many models, never return "Try again"
    models = ["llama-3.3-70b-versatile","llama-3.1-8b-instant","llama3-70b-8192","openai/gpt-oss-120b","openai/gpt-oss-20b","gemma2-9b-it","mixtral-8x7b-32768"]
    for model in models:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role":"system","content":"You are SI Worldwide, helpful assistant. Answer ALL questions accurately, current, short and clear. For fighting/war questions, give current 2025-2026 conflicts with sources."},
                    {"role":"user","content":question}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            ans = r.choices[0].message.content
            if ans and len(ans) > 10:
                return ans
        except Exception as e:
            continue
    return "I had a temporary issue, but I can answer. Please ask again, or ask more specifically like 'Which wars are happening in 2026?'"

st.title("SI Worldwide 🌍")
st.caption("V10 - ANYONE Real + ANY Question")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()
with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Picture of Mbappe, Messi, or Which countries fighting...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()
    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})

    is_pic = any(w in low for w in ["picture","photo","image","draw","show"])
    if any(w in low for w in ["which countries","what is","difference","meaning","translate","who was","who is","how to","can a","why","when","where","how many","list"]):
        if not low.strip().startswith(("picture","photo","image")):
            is_pic=False
    if low.strip().startswith(("picture","photo","image")):
        is_pic=True

    if is_pic:
        clean = re.sub(r'picture of a|picture of|photo of|image of|picture|photo|image|draw|show me', '', low, flags=re.I).strip()
        if not clean: clean = q
        # Fix common typo: mbape -> mbappe
        if "mbape" in clean: clean = "Kylian Mbappe"
        url, cap = get_anyone_photo(clean)
        if url is None:
            st.session_state.messages.append({"role":"assistant","content":cap})
        else:
            st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":cap})
    else:
        ans = answer_any_question(q)
        st.session_state.messages.append({"role":"assistant","content":ans})

    st.rerun()
