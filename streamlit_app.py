import streamlit as st
import requests, os, datetime, unicodedata, urllib.parse

st.set_page_config(page_title="Stephen's Intelligence Worldwide", layout="wide")
st.markdown("<style>.stApp{background:#000}.stMarkdown p{color:white}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:white'>INTELLIGENCE WORLDWIDE V7.3</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#888'>Always There - Ghana - Answers ANY Question</p>", unsafe_allow_html=True)

def clean(t):
    try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    except: return t

def get_key():
    try: return str(st.secrets.get("GROQ_API_KEY","")).strip()
    except: return ""

HEADERS = {"User-Agent": "SI-Worldwide/7.3 Ghana"}

def get_live_context(q):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json"
        r = requests.get(url, headers=HEADERS, timeout=6).json()
        if not r.get("query",{}).get("search"): return ""
        title = r["query"]["search"][0]["title"]
        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        sr = requests.get(sum_url, headers=HEADERS, timeout=6).json()
        extract = sr.get("extract","")
        if extract: return f"LIVE Wikipedia: {extract[:900]}"
    except: pass
    return ""

def ask(q,h):
    k=get_key()
    if not k or len(k) < 10:
        return "ERROR: GROQ_API_KEY missing. Add it in Streamlit > Settings > Secrets"

    today = datetime.date.today().strftime("%B %d, %Y")
    live = get_live_context(q)

    system_prompt = f"""You are Stephen's Intelligence V7.3. Today is {today}. Year 2026.
LIVE FACTS: {live}
FACTS: Pope Leo XIV is current pope (elected May 8 2025, Francis died April 21 2025).
You answer ANY question correctly. Explain CV means Curriculum Vitae etc. Be short, friendly, Ghana style."""

    m=[{"role":"system","content":system_prompt}]
    for r,msg in h[-6:]:
        if r in ["u","a"] and isinstance(msg, str) and len(msg) < 700 and not msg.endswith(".png"):
            m.append({"role":"user" if r=="u" else "assistant","content":clean(msg)})
    m.append({"role":"user","content":clean(q)})

    try:
        # FIXED MODEL NAME - This one exists!
        resp=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {k}", "Content-Type":"application/json"},
            json={"model":"llama-3.1-8b-instant","messages":m,"temperature":0.3}, timeout=30)
        j=resp.json()
        if "choices" not in j:
            return f"Groq Error: {j}. Check your GROQ_API_KEY."
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def make_image(prompt):
    try:
        low = prompt.lower()
        if "samson" in low and "long hair" not in low:
            prompt += ", long hair, ancient Israelite, muscular, biblical"
        safe_prompt = urllib.parse.quote(prompt + ", ultra detailed, 8k, cinematic")
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
        r = requests.get(url, timeout=90, headers=HEADERS)
        if r.status_code == 200 and len(r.content) > 5000:
            with open("output.png","wb") as f: f.write(r.content)
            return "output.png"
    except: pass
    return None

if "history" not in st.session_state: st.session_state.history = []
for role,msg in st.session_state.history:
    if role=="u": st.markdown(f"**🔴 You:** {msg}")
    else:
        if isinstance(msg, str) and os.path.exists(msg) and msg.endswith(".png"): st.image(msg)
        else: st.markdown(f"**🟠 SI V7.3:** {msg}")

st.divider()
q = st.text_input("Ask ANYTHING or Draw...", placeholder="What's the meaning of CV?", key="qinput")
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
            if img: st.session_state.history.append(("a", img))
            else:
                ans = ask(q, st.session_state.history)
                st.session_state.history.append(("a", ans))
    else:
        with st.spinner("Answering..."):
            ans = ask(q, st.session_state.history)
            st.session_state.history.append(("a", ans))
    st.rerun()
