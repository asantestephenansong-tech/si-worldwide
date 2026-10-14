import streamlit as st
import requests, urllib.parse, random, unicodedata

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide")
st.caption("Ask anything • Images • Unlimited")

def clean(t):
    try:
        return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    except:
        return t

def get_key():
    try:
        k=st.secrets.get("GROQ_API_KEY","")
        return str(k).strip().replace('"','').replace("'","")
    except:
        return ""

def ask(q):
    k=get_key()
    if not k.startswith("gsk_"):
        return "Add GROQ_API_KEY in Streamlit Secrets first! Go to Manage app > Settings > Secrets and paste GROQ_API_KEY = \"gsk_...\""
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
            json={"model":"openai/gpt-oss-20b"},"messages":[{"role":"system","content":"You are SI Worldwide AI"},{"role":"user","content":clean(q)}],"temperature":0.7,"max_tokens":1024},timeout=30)
        if r.status_code==200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Groq error {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return f"Error: {e}"

def img_url(p):
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote_plus(p)}?width=512&height=512&nologo=true&seed={random.randint(1,999999)}"

k=get_key()
if k.startswith("gsk_"):
    st.sidebar.success("✅ Brain Connected")
else:
    st.sidebar.error("❌ No key")
    st.sidebar.info("Go to Streamlit > Manage app > Settings > Secrets\nPaste:\nGROQ_API_KEY = \"gsk_...\"")

if "ch" not in st.session_state:
    st.session_state.ch=[]

q=st.chat_input("Ask anything...")
if q:
    st.session_state.ch.append(("u",q))
    a=ask(q)
    st.session_state.ch.append(("a",a))
    if any(w in q.lower() for w in ["image","draw","picture","photo","generate"]):
        st.session_state.ch.append(("i",img_url(q)))

for r,m in st.session_state.ch:
    if r=="u":
        st.chat_message("user").write(m)
    elif r=="a":
        st.chat_message("assistant").write(m)
    else:
        st.image(m)

if st.button("Clear Chat"):
    st.session_state.ch=[]
    st.rerun()
