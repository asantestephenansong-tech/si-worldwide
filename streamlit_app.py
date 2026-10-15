import streamlit as st
import requests, urllib.parse, random, unicodedata, os

st.set_page_config(page_title="Stephen's Intelligence", page_icon="🌟", layout="centered")
st.markdown("""<style>.stApp{background:#000} h1{color:#D4AF37!important;text-align:center} p{color:#CCC!important}</style>""", unsafe_allow_html=True)

if os.path.exists("logo.png"):
 c1,c2,c3=st.columns([1,1.2,1])
 with c2: st.image("logo.png", use_container_width=True)

st.markdown("<h1>STEPHEN'S INTELLIGENCE</h1><p style='text-align:center;color:#D4AF37!important'>Draw ANYONE • ANYTHING • ANY ANIMAL 🇬🇭</p>", unsafe_allow_html=True)

def clean(t):
 try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
 except: return t

def get_key():
 try: return str(st.secrets.get("GROQ_API_KEY","")).strip().replace('"','')
 except: return ""

def ask(q, hist):
 k=get_key()
 msgs=[{"role":"system","content":"You are Stephen's Intelligence. Short answers."}]
 for r,m in hist[-6:]:
  if r in ["u","a"]: msgs.append({"role":"user" if r=="u" else "assistant","content":m})
 msgs.append({"role":"user","content":clean(q)})
 try:
  r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"}, json={"model":"openai/gpt-oss-20b","messages":msgs,"max_tokens":500}, timeout=30)
  return r.json()["choices"][0]["message"]["content"]
 except: return "Try again"

def make_image(prompt):
 # UNIVERSAL - ANYTHING
 p=clean(prompt).strip()
 # Remove only the command words, keep EVERYTHING else
 for w in ["image of","picture of","photo of","draw an image of","draw a","draw","generate an image of","create an image of","create a","create","show me","make a pic of","make an image of"]:
  if p.lower().startswith(w):
   p=p[len(w):].strip()
 if not p: p="beautiful scene"
 # Universal quality booster for ANYTHING
 booster="ultra realistic, highly detailed, 8k, cinematic, sharp focus, vibrant, professional photography"
 full=f"{p}, {booster}"
 safe=urllib.parse.quote_plus(full)
 # STABLE URL - works for anyone, anything, any animal
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999999)}"

if "ch" not in st.session_state: st.session_state.ch=[]

for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else: st.chat_message("assistant").image(m, caption=f"SI Image: {m[:30]}... 🎨")

q=st.chat_input("Draw ANYONE, ANYTHING, ANY ANIMAL... just type 'draw a...'")
if q:
 ql=q.lower()
 is_image=any(w in ql for w in ["draw","image","picture","photo","generate","create","paint","show me","make a pic"])
 st.session_state.ch.append(("u",q))
 if is_image:
  st.session_state.ch.append(("a",f"Creating: {q} 🎨"))
  st.session_state.ch.append(("i",make_image(q)))
 else:
  st.session_state.ch.append(("a",ask(q, st.session_state.ch)))
 st.rerun()

if st.button("Clear Chat ✨"): st.session_state.ch=[]; st.rerun()
