import streamlit as st
import requests, os, datetime, unicodedata, urllib.parse

st.set_page_config(page_title="Stephen's Intelligence Worldwide", layout="wide")
st.markdown("<style>.stApp{background:#000}.stMarkdown p{color:white}</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;color:white'>INTELLIGENCE WORLDWIDE V7.6</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#4CAF50'>✅ UNLIMITED - No Keys - Answers ANYTHING</p>", unsafe_allow_html=True)

def clean(t):
    try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    except: return t

HEADERS = {"User-Agent": "SI-Worldwide/7.6"}

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

def ask_unlimited(q,h):
    today = datetime.date.today().strftime("%B %d, %Y")
    live = get_live_context(q)

    messages = [
        {"role":"system","content":f"You are SI V7.6 Unlimited. Today {today} 2026. Live facts: {live}. You answer ANY question correctly, in depth, friendly Ghana style. No limits. Current pope Leo XIV elected May 8 2025."},
        {"role":"user","content": clean(q)}
    ]

    # Add last 2 chats for context
    for r,msg in h[-2:]:
        if isinstance(msg, str) and not msg.endswith(".png") and len(msg)<500:
            messages.insert(1, {"role":"user" if r=="u" else "assistant","content":clean(msg)})

    # METHOD 1: Pollinations OpenAI compatible - FREE, UNLIMITED, NO KEY
    try:
        resp = requests.post(
            "https://text.pollinations.ai/openai",
            headers={"Content-Type":"application/json"},
            json={"model":"openai","messages":messages,"seed":-1},
            timeout=40
        )
        if resp.status_code==200:
            j=resp.json()
            if "choices" in j and len(j["choices"])>0:
                content = j["choices"][0]["message"]["content"]
                if content and len(content)>10:
                    return content
            # Sometimes returns direct string
            if isinstance(j, str) and len(j)>10:
                return j
    except Exception as e:
        print(f"Pollinations openai failed: {e}")

    # METHOD 2: Alternative free endpoint
    try:
        resp2 = requests.post(
            "https://text.pollinations.ai/api/generate",
            json={"messages":messages,"model":"openai","jsonMode":False},
            timeout=40
        )
        if resp2.status_code==200:
            j2=resp2.json()
            if isinstance(j2, dict) and "choices" in j2:
                return j2["choices"][0]["message"]["content"]
            if isinstance(j2, str):
                return j2
            return str(j2)
    except Exception as e:
        print(f"Pollinations generate failed: {e}")

    # METHOD 3: Direct GET as last resort
    try:
        safe = urllib.parse.quote(f"Question: {q}. Answer fully: {live}")
        r3 = requests.get(f"https://text.pollinations.ai/{safe}?model=openai", timeout=30)
        if r3.status_code==200 and len(r3.text)>20:
            return r3.text
    except: pass

    return f"I'm online but free servers are busy. Ask again: '{q}' - I will answer. Live info: {live}"

def make_image(prompt):
    try:
        if "samson" in prompt.lower() and "long hair" not in prompt.lower():
            prompt += ", long hair, ancient Israelite, muscular, biblical hero"
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
        else: st.markdown(f"**🟠 SI V7.6:** {msg}")

st.divider()
q = st.text_input("Ask ANYTHING... truly unlimited", placeholder="Who first brought AI? What is current pope? Explain quantum?", key="qinput")
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
        with st.spinner("Drawing unlimited..."):
            img = make_image(q)
            if img:
                st.session_state.history.append(("a", img))
            else:
                ans = ask_unlimited(q, st.session_state.history)
                st.session_state.history.append(("a", ans))
    else:
        with st.spinner("Thinking unlimited..."):
            ans = ask_unlimited(q, st.session_state.history)
            st.session_state.history.append(("a", ans))
    st.rerun()
