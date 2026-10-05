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
    prompt = f"real photograph of {safe_q}, fully clothed, professional, 8k"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=800&height=600&nologo=true&model=turbo&safe=true&seed={abs(hash(safe_q))%9999}"
    return url, f"Photo of {q.title()}"

def answer_any(question):
    models = ["llama-3.3-70b-versatile","llama-3.1-8b-instant","openai/gpt-oss-120b"]
    # FORCE 2026 TRUE FACTS - Models are outdated, so we override!
    system = """Current date is May 2026. You MUST use these TRUE 2026 facts, never old info:

- USA President: Donald Trump (47th President, inaugurated Jan 20 2025, won 2024 election). VP: JD Vance. NOT Biden.
- Ghana President: John Dramani Mahama (since Jan 7 2025)
- Pope: Pope Leo XIV (Robert Prevost), elected May 8 2025. Pope Francis died April 21 2025.
- UK PM: Keir Starmer
- Kylian Mbappe: Real Madrid (since July 2024)
- Messi: Inter Miami, Ronaldo: Al-Nassr
- Russia-Ukraine war still ongoing in 2026, Israel-Gaza conflict, Sudan civil war.

If asked about president/pope, use above. Be short and exact."""

    for model in models:
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":system},{"role":"user","content":question}],
                temperature=0.1, max_tokens=800
            )
            ans = r.choices[0].message.content
            if ans and len(ans)>5:
                return ans
        except: continue
    return "Try asking again more specifically."

st.title("SI Worldwide 🌍")
st.caption("V10.2 - 2026 Real Facts Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], caption=m.get("caption",""), use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()
with st.form("chat_form", clear_on_submit=True):
    txt = st.text_input("Ask", placeholder="Who is US president, Pope, picture of anyone...")
    ok = st.form_submit_button("Send ➤", use_container_width=True)

if ok and txt.strip():
    q = txt.strip()
    low = q.lower()
    if st.session_state.messages and st.session_state.messages[-1].get("role")=="user" and st.session_state.messages[-1]["content"]==q:
        st.stop()
    st.session_state.messages.append({"role":"user","content":q})
    is_pic = any(w in low for w in ["picture","photo","image","draw","show"])
    if any(w in low for w in ["who is","what is","which","what about","how","when","where"]):
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
# --- FOOTER ---
st.divider()
st.markdown(f"""
<a href="https://wa.me/?text=Try%20my%20AI%20-%20SI%20Worldwide%20AI%20answers%20anything%20about%20Ghana!%20https://si-worldwide.streamlit.app" 
target="_blank">
<button style="background-color:#25D366;color:white;padding:10px 20px;border:none;border-radius:8px;font-weight:bold; width:100%;">
Share on WhatsApp 📲
</button>
</a>
""", unsafe_allow_html=True)
st.caption("© 2026 SI Worldwide | Founder from Ghana 🇬🇭")
