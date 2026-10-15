import streamlit as st
import requests, os, datetime, unicodedata

st.set_page_config(page_title="Stephen's Intelligence Worldwide", layout="wide")
st.markdown("<style>.stApp{background:#000} h1,h2,h3,p{color:white}</style>", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    c1,c2,c3=st.columns([1,1.2,1])
    with c2: st.image("logo.png", use_container_width=True)
st.markdown("<h1 style='text-align:center'>STEPHEN'S INTELLIGENCE WORLDWIDE V7.2</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaa'>Always There - Answers Any Question Correctly - Ghana 🇬🇭</p>", unsafe_allow_html=True)

def clean(t):
    try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    except: return t

def get_key():
    try: return str(st.secrets.get("GROQ_API_KEY",""))
    except: return ""

HEADERS = {"User-Agent": "SI-Worldwide/7.2 Ghana"}

# --- NEW: LIVE INTERNET SEARCH FOR ANY QUESTION ---
def get_live_context(q):
    try:
        # Search Wikipedia for live facts
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json"
        r = requests.get(url, headers=HEADERS, timeout=6).json()
        if not r.get("query",{}).get("search"):
            return ""
        hit = r["query"]["search"][0]
        title = hit["title"]
        # Get summary
        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        sr = requests.get(sum_url, headers=HEADERS, timeout=6).json()
        extract = sr.get("extract","")
        if extract:
            return f"LIVE WIKIPEDIA for '{q}': {extract[:800]} (Source: {title})"
    except:
        pass
    return ""

def ask(q,h):
    k=get_key()
    today = datetime.date.today().strftime("%B %d, %Y")
    live = get_live_context(q)

    system_prompt = f"""You are Stephen's Intelligence Worldwide V7.2.
Today is {today}. You are in Accra, Ghana. Current year is 2026.

LIVE FACTS FROM INTERNET:
{live}

CRITICAL PERMANENT FACTS:
- Current Pope is Pope Leo XIV (Robert Francis Prevost, American from Chicago, born Sept 14 1955, elected May 8 2025, Order of Saint Augustine). Pope Francis died April 21 2025.
- Current US President is Donald Trump (2nd term started Jan 20 2025).
- Always use live facts + permanent facts above. Never say you are cut off in 2023.

RULES:
- Answer ANY question with correct, up-to-date info.
- If user wants to draw / picture / image, you still answer but say you will create it.
- Be short, friendly, Ghana vibe. No long essay.
"""

    m=[{"role":"system","content":system_prompt}]
    for r,msg in h[-6:]:
        if r in ["u","a"] and isinstance(msg, str) and len(msg) < 600 and not msg.startswith("/"):
            m.append({"role":"user" if r=="u" else "assistant","content":clean(msg)})
    m.append({"role":"user","content":clean(q)})

    try:
        resp=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {k}", "Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":m,"temperature":0.3}, timeout=30)
        j=resp.json()
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Try again - {str(e)[:150]}"

BIBLE_WORDS = ["bible","abraham","isaac","jacob","samson","david","goliath","moses","jesus","noah"]

def get_wiki_photo(name):
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={name}&format=json"
        sr = requests.get(search_url, headers=HEADERS, timeout=8).json()
        if not sr.get("query",{}).get("search"): return None
        title = sr["query"]["search"][0]["title"]
        img_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={title}&pithumbsize=500&format=json"
        jr = requests.get(img_url, headers=HEADERS, timeout=8).json()
        pages = jr.get("query",{}).get("pages",{})
        for pid in pages:
            if "thumbnail" in pages[pid]: return pages[pid]["thumbnail"]["source"]
    except: pass
    return None

def make_image(prompt):
    try:
        HF_KEY = st.secrets.get("HF_API_KEY","")
        if not HF_KEY: return None
        low = prompt.lower()
        # Bible & Jersey fixes from V7.0
        if "samson" in low and "long hair" not in low:
            prompt += ", long hair, ancient Israelite, muscular, biblical hero"
        if "david" in low and "goliath" in low:
            prompt += ", young shepherd boy with sling, no armor, biblical"

        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_KEY}"}
        r = requests.post(API_URL, headers=headers, json={"inputs": prompt + ", ultra detailed, 8k, cinematic, high quality"}, timeout=90)
        if r.status_code == 200:
            with open("output.png","wb") as f: f.write(r.content)
            return "output.png"
        else:
            # Fallback to SDXL
            API_URL2 = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            r2 = requests.post(API_URL2, headers=headers, json={"inputs": prompt}, timeout=90)
            if r2.status_code == 200:
                with open("output.png","wb") as f: f.write(r2.content)
                return "output.png"
    except Exception as e:
        st.error(f"Image error: {e}")
    return None

# --- UI HISTORY ---
if "history" not in st.session_state:
    st.session_state.history = []

for role,msg in st.session_state.history:
    if role=="u":
        st.markdown(f"**🔴 You:** {msg}")
    else:
        if isinstance(msg, str) and (msg.endswith(".png") and os.path.exists(msg)):
            st.image(msg, caption="SI V7.2 Generated")
        elif isinstance(msg, str) and msg.startswith("http") and ".jpg" in msg or ".png" in msg or "upload.wikimedia" in msg:
            st.image(msg, caption="SI V7.2")
        else:
            st.markdown(f"**🟠 SI V7.2:** {msg}")

st.divider()
q = st.text_input("Ask ANYTHING or say 'draw...' — V7.2 knows 2026", placeholder="Who is current pope? Draw Samson...")

col1,col2=st.columns([3,1])
with col1:
    send = st.button("Send ✨", type="primary", use_container_width=True)
with col2:
    clear = st.button("Clear Chat", use_container_width=True)

if clear:
    st.session_state.history=[]
    st.rerun()

if send and q:
    st.session_state.history.append(("u", q))
    low = q.lower()

    # If user wants image
    if any(x in low for x in ["draw","picture","create image","generate image","photo of","image of","create a"]):
        with st.spinner("SI V7.2 Creating image..."):
            img = make_image(q)
            if img:
                st.image(img, caption="SI V7.2")
                st.session_state.history.append(("a", img))
            else:
                ans = ask(q, st.session_state.history)
                st.markdown(f"🟠 {ans}")
                st.session_state.history.append(("a", ans))
    else:
        # Chat - uses live search
        with st.spinner("SI V7.2 Searching live knowledge..."):
            ans = ask(q, st.session_state.history)
            st.markdown(f"🟠 {ans}")
            st.session_state.history.append(("a", ans))
    st.rerun()

st.divider()
st.caption("V7.2 Universal Knowledge | Always There | Ghana 🇬🇭 | si-worldwide.streamlit.app")
