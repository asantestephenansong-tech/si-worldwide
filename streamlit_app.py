import streamlit as st
import requests, urllib.parse, random, unicodedata

st.set_page_config(page_title="SI Worldwide", layout="centered")
st.title("🌍 SI Worldwide")
st.caption("Ask anything • Short & Smart")

def clean(t):
 try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
 except: return t

def get_key():
 try:
  k=st.secrets.get("GROQ_API_KEY","")
  return str(k).strip().replace('"','').replace("'","")
 except: return ""

def ask(q, history):
 k=get_key()
 if not k.startswith("gsk_"): return "Add GROQ_API_KEY in Streamlit Secrets!"
 try:
  msgs=[{"role":"system","content":"You are SI Worldwide. Give short clear answers in 2-4 sentences. No HTML tags. Remember conversation context."}]
  for r,m in history[-4:]:
   if r!="i":
    msgs.append({"role":"user" if r=="u" else "assistant","content":m})
  msgs.append({"role":"user","content":clean(q)})
  r=requests.post("https://api.groq.com/openai/v1/chat/completions",
   headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"},
   json={"model":"openai/gpt-oss-20b","messages":msgs,"max_tokens":300},
   timeout=30)
  j=r.json()
  return j["choices"][0]["message"]["content"] if r.status_code==200 else f"Error: {j}"
 except Exception as e: return f"Error: {e}"

def img_url(p): return f"https://image.pollinations.ai/prompt/{urllib.parse.quote_plus(p)}?width=512&height=512&nologo=true&seed={random.randint(1,999999)}"

k=get_key()
if k.startswith("gsk_"): st.sidebar.success("✅ Connected")
else: st.sidebar.error("❌ Add GROQ_API_KEY")

if "ch" not in st.session_state: st.session_state.ch=[]
q=st.chat_input("Ask anything...")
if q:
 a=ask(q, st.session_state.ch)
 st.session_state.ch.append(("u",q))
 st.session_state.ch.append(("a",a))
 if any(w in q.lower() for w in ["image","draw","picture","photo"]):
  st.session_state.ch.append(("i",img_url(q)))
 st.rerun()

for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else: st.image(m)

if st.button("Clear Chat"): st.session_state.ch=[]; st.rerun()
