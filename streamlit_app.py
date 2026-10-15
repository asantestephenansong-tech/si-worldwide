import streamlit as st, requests, urllib.parse, random, unicodedata, os
st.set_page_config(page_title="Stephen's Intelligence", page_icon="🌟", layout="centered")
st.markdown("<style>.stApp{background:#000} h1{color:#D4AF37!important;text-align:center}</style>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
 c1,c2,c3=st.columns([1,1.2,1])
 with c2: st.image("logo.png", use_container_width=True)
st.markdown("<h1>STEPHEN'S INTELLIGENCE</h1><p style='text-align:center;color:#D4AF37'>V6.4 REAL FIX</p>", unsafe_allow_html=True)

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

HEADERS = {"User-Agent": "SI-Worldwide/6.4 Ghana"}
BAD_WORDS = ["pig","dog","cat","elephant","lion","tiger","boys fighting","fighting","fight"]

def get_real_photo(name):
 try:
  low=name.lower()
  for w in BAD_WORDS:
   if w in low: return None
  if len(name.split())>4: return None
  # Search
  search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(name)}&format=json"
  sr = requests.get(search_url, headers=HEADERS, timeout=8).json()
  if not sr.get("query",{}).get("search"): return None
  title = sr["query"]["search"][0]["title"]
  sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
  r = requests.get(sum_url, headers=HEADERS, timeout=8).json()
  if "originalimage" in r: return r["originalimage"]["source"]
  if "thumbnail" in r: return r["thumbnail"]["source"]
 except: pass
 return None

def make_image(prompt):
 p=clean(prompt).strip()
 low=p.lower()
 for w in ["picture of","image of","photo of","draw an image of","draw a","draw","generate an image of","create an image of","create","show me","make a pic of"]:
  if low.startswith(w):
   p=p[len(w):].strip(); low=p.lower()
 if not p: p="beautiful landscape"
 if "fight" in low:
  p="two boys playing friendly soccer together smiling, joyful"
 # Try REAL
 real = get_real_photo(p)
 if real: return real
 # AI fallback - single person, safe
 safe=urllib.parse.quote_plus(f"{p}, solo portrait, photorealistic, 8k, single person only")
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}"

if "ch" not in st.session_state: st.session_state.ch=[]
for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else:
  try: st.chat_message("assistant").image(m, caption="SI V6.4")
  except: st.chat_message("assistant").markdown(f"![image]({m})")

q=st.chat_input("Try: Shatta Wale, Kwame Nkrumah, John Mahama...")
if q:
 ql=q.lower()
 is_img=any(w in ql for w in ["draw","image","picture","photo","generate","create","paint","show me","make a pic"])
 st.session_state.ch.append(("u",q))
 if is_img:
  st.session_state.ch.append(("a",f"V6.4 Creating: {q} 🎨"))
  st.session_state.ch.append(("i",make_image(q)))
 else:
  st.session_state.ch.append(("a",ask(q, st.session_state.ch)))
 st.rerun()
if st.button("Clear Chat ✨"): st.session_state.ch=[]; st.rerun()
