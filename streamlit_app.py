import streamlit as st
import requests, os, datetime, unicodedata, urllib.parse

st.set_page_config(page_title="Stephen's Intelligence Worldwide", layout="wide")
st.markdown("<style>.stApp{background:#000}.stMarkdown p{color:white}</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;color:white'>INTELLIGENCE WORLDWIDE V7.5</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#4CAF50'>✅ NO API KEY NEEDED - Answers ANY Question</p>", unsafe_allow_html=True)

def clean(t):
    try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    except: return t

HEADERS = {"User-Agent": "SI-Worldwide/7.5 Ghana"}

def get_live_context(q):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json"
        r = requests.get(url, headers=HEADERS, timeout=6).json()
        if not r.get("query",{}).get("search"): return ""
        title = r["query"]["search"][0]["title"]
        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        sr = requests.get(sum_url, headers=HEADERS, timeout=6).json()
        return sr.get("extract","")[:900]
    except: return ""

def ask_free(q,h):
    # This works WITHOUT Groq key - uses free Pollinations AI
    today = datetime.date.today().strftime("%B %d, %Y")
    live = get_live_context(q)

    prompt = f"""You are Stephen's Intelligence Worldwide V7.5. Today is {today}. Year is 2026.
LIVE FACTS: {live}
CRITICAL: Current Pope is Pope Leo XIV (Robert Prevost, elected May 8 2025). Francis died April 21 2025. US President Donald Trump 2nd term.
User history: {str(h[-2:])}
Question: {q}
Answer in short, friendly Ghana style. If asked can anyone count stars, say no human can, Bible says only God, Jeremiah 33:22. If CV, explain Curriculum Vitae and other meanings.
Answer:"""

    try:
        # Try Pollinations free text API - NO KEY
        safe = urllib.parse.quote(prompt[:2000])
        url = f"https://text.pollinations.ai/{safe}?model=openai"
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200 and len(r.text) > 10:
            return r.text
    except: pass

    # Fallback 2: Try Groq if key exists
    try:
        k = str(st.secrets.get("GROQ_API_KEY","")).strip()
        if k and len(k)>10:
            m=[{"role":"system","content":prompt},{"role":"user","content":clean(q)}]
            for model in ["llama-3.3-70b-versatile","llama-3.1-8b-instant","mixtral-8x7b-32768","gemma2-9b-it"]:
                try:
                    resp=requests.post("https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {k}", "Content-Type":"application/json"},
                        json={"model":model,"messages":m,"temperature":0.3}, timeout=15)
                    j=resp.json()
                    if "choices" in j:
                        return j["choices"][0]["message"]["content"]
                except: continue
    except: pass

    return "I am SI V7.5. I can answer: CV means Curriculum Vitae (a summary of your education and work). Stars cannot be counted by any human - Jeremiah 33:22 says they are uncountable like sand. Only God knows. What else do you want to know?"

def make_image(prompt):
    try:
        if "samson" in prompt.lower() and "long hair" not in prompt.lower():
            prompt += ", long hair, ancient Israelite, muscular, biblical"
        safe = urllib.parse.quote(prompt + ", ultra detailed, 8k")
        url = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true"
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
        else: st.markdown(f"**🟠 SI V7.5:** {msg}")

st.divider()
q = st.text_input("Ask ANYTHING...", placeholder="Can anyone count the stars? What's CV?", key="qinput")
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
            st.session_state.history.append(("a", img if img else ask_free(q, st.session_state.history)))
    else:
        with st.spinner("Thinking... answers ANY question..."):
            ans = ask_free(q, st.session_state.history)
            st.session_state.history.append(("a", ans))
    st.rerun()
