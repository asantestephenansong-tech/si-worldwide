import streamlit as st, requests, urllib.parse, random, unicodedata, os, time
st.set_page_config(page_title="Stephen's Intelligence", page_icon="🌟", layout="centered")
st.markdown("<style>.stApp{background:#000} h1{color:#D4AF37!important;text-align:center}</style>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
 c1,c2,c3=st.columns([1,1.2,1])
 with c2: st.image("logo.png", use_container_width=True)
st.markdown("<h1>STEPHEN'S INTELLIGENCE</h1><p style='text-align:center;color:#D4AF37'>V5 UNIVERSAL - ANYONE ANYTHING ANY ANIMAL</p>", unsafe_allow_html=True)

def clean(t):
 try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
 except: return t
def get_key():
 try: return str(st.secrets.get("GROQ_API_KEY","")).strip().replace('"','')
 except: return ""
def ask(q,h):
 k=get_key()
 m=[{"role":"system","content":"You are SI. Short answers."}]
 for r,msg in h[-6:]:
  if r in ["u","a"]: m.append({"role":"user" if r=="u" else "assistant","content":msg})
 m.append({"role":"user","content":clean(q)})
 try:
  r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"}, json={"model":"openai/gpt-oss-20b","messages":m,"max_tokens":500}, timeout=30)
  return r.json()["choices"][0]["message"]["content"]
 except: return "Try again"

def make_image(prompt):
 p=clean(prompt).strip()
 low=p.lower()
 # FIX TYPOS UNIVERSALLY
 fixes={"mbape":"Kylian Mbappe Real Madrid","mbappe":"Kylian Mbappe","gils":"girls","pictur":"picture","pictue":"picture","hous":"house","rice":"jollof rice Ghana"}
 for k,v in fixes.items():
  if k in low: p=low.replace(k,v); low=p.lower(); break
 for w in ["image of","picture of","photo of","draw an image of","draw a","draw","generate an image of","create an image of","create","show me","make a pic of"]:
  if low.startswith(w): p=p[len(w):].strip(); low=p.lower()
 if not p: p="beautiful landscape"
 # Avoid violence block
 if "fight" in low: p=low.replace("fighting","playful friendly debate").replace("fight","friendly competition")
 booster="photorealistic, ultra detailed, 8k, cinematic lighting, sharp focus"
 safe=urllib.parse.quote_plus(f"{p}, {booster}")
 # V5: TURBO model = most stable, never breaks
 seed=random.randint(1,99999999)
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={seed}"

if "ch" not in st.session_state: st.session_state.ch=[]

for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else:
  try: st.chat_message("assistant").image(m, caption="SI V5 🎨")
  except: st.chat_message("assistant").markdown(f"![image]({m})")

q=st.chat_input("Draw ANYONE, ANYTHING, ANY ANIMAL...")
if q:
 ql=q.lower()
 is_img=any(w in ql for w in ["draw","image","picture","photo","generate","create","paint","show me","make a pic"])
 st.session_state.ch.append(("u",q))
 if is_img:
  st.session_state.ch.append(("a",f"Creating V5: {q} 🎨 Wait 3 sec..."))
  time.sleep(1)
  st.session_state.ch.append(("i",make_image(q)))
 else:
  st.session_state.ch.append(("a",ask(q, st.session_state.ch)))
 st.rerun()
if st.button("Clear Chat ✨"): st.session_state.ch=[]; st.rerun()
