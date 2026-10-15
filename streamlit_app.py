import streamlit as st, requests, urllib.parse, random, unicodedata, os, datetime
st.set_page_config(page_title="Stephen's Intelligence", page_icon="🌟", layout="centered")
st.markdown("<style>.stApp{background:#000} h1{color:#D4AF37!important;text-align:center}</style>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
 c1,c2,c3=st.columns([1,1.2,1])
 with c2: st.image("logo.png", use_container_width=True)
st.markdown("<h1>STEPHEN'S INTELLIGENCE</h1><p style='text-align:center;color:#D4AF37'>V7.0 FINAL</p>", unsafe_allow_html=True)

def clean(t):
 try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
 except: return t
def get_key():
 try: return str(st.secrets.get("GROQ_API_KEY","")).strip().replace('"','')
 except: return ""
def ask(q,h):
 k=get_key()
 today = datetime.date.today().strftime("%B %Y")
 system_prompt = f"You are Stephen's Intelligence, Ghana. Today is {today}. Mbappe=Real Madrid since June 2024. Use 2026 knowledge. If asked Bible age: Sarah died at 127 years old (Genesis 23:1). Short answers."
 m=[{"role":"system","content":system_prompt}]
 for r,msg in h[-6:]:
  if r in ["u","a"]: m.append({"role":"user" if r=="u" else "assistant","content":msg})
 m.append({"role":"user","content":clean(q)})
 try:
  r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"}, json={"model":"openai/gpt-oss-20b","messages":m,"max_tokens":500}, timeout=30)
  return r.json()["choices"][0]["message"]["content"]
 except: return "Try again"

HEADERS = {"User-Agent": "SI-Worldwide/7.0 Ghana"}
BIBLE_WORDS = ["bible","abraham","isaac","jacob","joseph","moses","david","goliath","samson","daniel","solomon","esther","ruth","mary","peter","paul","adam","eve","noah","jesus","christ","jonah","job","ark","golgotha","calvary","saul","joshua","sarah","sara","maria","lazarus","martha"]

def get_wiki_photo(name):
 try:
  search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(name)}&format=json"
  sr = requests.get(search_url, headers=HEADERS, timeout=10).json()
  if not sr.get("query",{}).get("search"): return None
  title = sr["query"]["search"][0]["title"]
  img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1024"
  jr = requests.get(img_url, headers=HEADERS, timeout=10).json()
  pages = jr.get("query",{}).get("pages",{})
  for pid in pages:
   if "thumbnail" in pages[pid]: return pages[pid]["thumbnail"]["source"]
 except: pass
 return None

def make_image(prompt):
 p=clean(prompt).strip()
 low=p.lower()
 for w in ["picture of","image of","photo of","draw an image of","draw a","draw","generate an image of","create an image of","create","show me","make a pic of","bible story of","story of"]:
  if low.startswith(w):
   p=p[len(w):].strip(); low=p.lower()
 if not p: p="beautiful landscape"
 is_bible = any(b in low for b in BIBLE_WORDS)
 if is_bible:
  safe_p = p.replace("crucified","on the cross at Golgotha")
  if "cross" in low and "jesus" in low:
   biblical_prompt = f"reverent biblical painting of Jesus Christ on the cross at Golgotha, three crosses on hill, ancient Jerusalem sunset, holy reverent not graphic, oil painting cinematic 8k"
  elif "david" in low and "goliath" in low:
   biblical_prompt = f"epic biblical scene David young shepherd boy facing giant Goliath warrior with spear and shield, Valley of Elah, David with sling, cinematic dramatic light, 8k"
  else:
   biblical_prompt = f"epic biblical movie scene of {safe_p}, ancient Israel middle eastern people biblical robes, dramatic holy light, reverent detailed oil painting 8k"
  safe=urllib.parse.quote_plus(biblical_prompt)
  return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}"
 real = get_wiki_photo(p)
 if real: return real
 safe=urllib.parse.quote_plus(f"{p}, photorealistic real photo 8k")
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}"

if "ch" not in st.session_state: st.session_state.ch=[]
for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else:
  try: st.chat_message("assistant").image(m, caption="SI V7.0")
  except: st.chat_message("assistant").markdown(f"![image]({m})")

q=st.chat_input("Ask or Draw... V7.0 Smart")
if q:
 ql=q.lower()
 # FIXED: Only if user says draw/picture/photo/image/generate/create/paint/show - NOT just "bible"
 is_img = any(w in ql for w in ["draw","picture","photo","image","generate","create","paint","show me","make a pic"])
 st.session_state.ch.append(("u",q))
 if is_img:
  st.session_state.ch.append(("a",f"V7.0 Creating: {q} 🎨"))
  st.session_state.ch.append(("i",make_image(q)))
 else:
  # Text question - answer it!
  st.session_state.ch.append(("a",ask(q, st.session_state.ch)))
 st.rerun()
if st.button("Clear Chat ✨"): st.session_state.ch=[]; st.rerun()
