import streamlit as st
import requests, os, datetime, unicodedata, urllib.parse

st.set_page_config(page_title="Stephen's Intelligence Worldwide", layout="wide")
st.markdown("<style>.stApp{background:#000}.stMarkdown p{color:white}</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;color:white'>INTELLIGENCE WORLDWIDE V7.7</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#4CAF50'>✅ HYBRID - Groq Turbo + Free Fallback</p>", unsafe_allow_html=True)

def clean(t):
    try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    except: return t

def get_key():
    try: return str(st.secrets.get("GROQ_API_KEY","")).strip()
    except: return ""

HEADERS = {"User-Agent": "SI-Worldwide/7.7"}

def get_live_context(q):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json"
        r = requests.get(url, headers=HEADERS, timeout=6).json()
        if not r.get("query",{}).get("search"): return ""
        title = r["query"]["search"][0]["title"]
        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        sr = requests.get(sum_url, headers=HEADERS, timeout=6).json()
        return sr.get("extract","")[:800]
    except: return ""

def ask_hybrid(q,h):
    today = datetime.date.today().strftime("%B %d, %Y")
    live = get_live_context(q)
    messages = [
        {"role":"system","content":f"You are SI V7.7 Hybrid. Today {today} 2026. Live facts: {live}. Answer ANY question correctly, detailed, Ghana friendly. Pope Leo XIV elected May 8 2025."},
        {"role":"user","content":clean(q)}
    ]
    for r,msg in h[-2:]:
        if isinstance(msg, str) and not msg.endswith(".png") and len(msg)<500:
            messages.insert(1, {"role":"user" if r=="u" else "assistant","content":clean(msg)})

    # TRY 1: GROQ if key exists (turbo fast)
    k = get_key()
    if k and len(k)>10:
        for model in ["llama-3.3-70b-versatile","llama-3.1-8b-instant","mixtral-8x7b-32768","gemma2-9b-it"]:
            try:
                resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {k}","Content-Type":"application/json"},
                    json={"model":model,"messages":messages,"temperature":0.3}, timeout=15)
                j=resp.json()
                if "choices" in j and len(j["choices"])>0:
                    return j["choices"][0]["message"]["content"] + f"\n\n_⚡ Groq {model}_"
            except: continue

    # TRY 2: FREE UNLIMITED - Pollinations (never dies)
    try:
        resp = requests.post("https://text.pollinations.ai/openai",
            headers={"Content-Type":"application/json"},
            json={"model":"openai","messages":messages,"seed":-1}, timeout=40)
        if resp.status_code==200:
            j=resp.json()
            if "choices" in j and len(j["choices"])>0:
                return j["choices"][0]["message"]["content"]
    except: pass

    # TRY 3: Final fallback
    try:
        safe = urllib.parse.quote(f"Answer: {q} Context: {live}")
        r3 = requests.get(f"https://text.pollinations.ai/{safe}?model=openai", timeout=30)
        if r3.status_code==200 and len(r3.text)>20:
            return r3.text
    except: pass

    return f"Live info: {live[:500]}"

def make_image(prompt):
    try:
        if "samson" in prompt.lower() and "long hair" not in prompt.lower():
            prompt += ", long hair, ancient Israelite, muscular, biblical"
        safe = urllib.parse.quote(prompt + ", ultra detailed, 8k cinematic")
        url = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&enhance=true"
        r = requests.get(url, timeout=90, headers=HEADERS)
        if r.status_code==200 and len(r.content)>5000:
            with open("output.png","wb") as f: f.write(r.content)
            return "output.png"
    except: pass
    return None

if "history" not in st.session_state: st.session_state.history = []
for role,msg in st.session_state.history:
    if role=="u": st.markdown(f"**🔴 You:** {msg}")
    else:
        if isinstance(msg, str) and os.path.exists(msg) and msg.endswith(".png"): st.image(msg)
        else: st.markdown(f"**🟠 SI V7.7:** {msg}")

st.divider()
q = st.text_input("Ask ANYTHING...", placeholder="Who first brought AI? Draw Samson?", key="qinput")
c1,c2 = st.columns([4,1])
with c1: send = st.button("Send ✨", type="primary", use_container_width=True)
with c2: clr = st.button("Clear", use_container_width=True)

if clr:
    st.session_state.history=[]
    st.rerun()
if send and q:
    st.session_state.history.append(("u", q))
    is_draw = any(x in q.lower() for x in ["draw","picture","create image","photo of","image of"])
    if is_draw:
        with st.spinner("Drawing..."):
            img = make_image(q)
            st.session_state.history.append(("a", img if img else ask_hybrid(q, st.session_state.history)))
    else:
        with st.spinner("Hybrid thinking..."):
            ans = ask_hybrid(q, st.session_state.history)
            st.session_state.history.append(("a", ans))
    st.rerun()
