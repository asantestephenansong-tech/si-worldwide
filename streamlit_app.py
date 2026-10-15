import streamlit as st, requests, urllib.parse, random, unicodedata, os
st.set_page_config(page_title="Stephen's Intelligence", page_icon="🌟", layout="centered")
st.markdown("<style>.stApp{background:#000} h1{color:#D4AF37!important;text-align:center}</style>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
 c1,c2,c3=st.columns([1,1.2,1])
 with c2: st.image("logo.png", use_container_width=True)
st.markdown("<h1>STEPHEN'S INTELLIGENCE</h1><p style='text-align:center;color:#D4AF37'>V6.7 ALL WORLDS</p>", unsafe_allow_html=True)

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

HEADERS = {"User-Agent": "SI-Worldwide/6.7 Ghana"}
BIBLE_WORDS = ["bible","david","goliath","moses","jesus","christ","noah","abraham","isaac","jacob","joseph","samson","daniel","solomon","esther","ruth","mary","peter","paul","adam","eve","cain","abel","gideon","elijah","elisha","jonah","job","ark","pharaoh","israelite","saul","joshua"]

def get_wiki_photo(name):
 try:
  search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(name)}&format=json"
  sr = requests.get(search_url, headers=HEADERS, timeout=10).json()
  if not sr.get("query",{}).get("search"): return None
  title = sr["query"]["search"][0]["title"]
  # Try to get page image that Streamlit can load
  img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1024"
  jr = requests.get(img_url, headers=HEADERS, timeout=10).json()
  pages = jr.get("query",{}).get("pages",{})
  for pid in pages:
   if "thumbnail" in pages[pid]:
    thumb = pages[pid]["thumbnail"]["source"]
    # test if image loads (https)
    if thumb.startswith("http"): return thumb
  # fallback to summary
  sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
  r = requests.get(sum_url, headers=HEADERS, timeout=10).json()
  if "originalimage" in r and "http" in r["originalimage"]["source"]:
   return r["originalimage"]["source"]
 except: pass
 return None

def make_image(prompt):
 p=clean(prompt).strip()
 low=p.lower()
 for w in ["picture of","image of","photo of","draw an image of","draw a","draw","generate an image of","create an image of","create","show me","make a pic of","bible story of"]:
  if low.startswith(w):
   p=p[len(w):].strip(); low=p.lower()
 if not p: p="beautiful landscape"

 # 1. BIBLE = AI BIBLICAL MOVIE STYLE
 is_bible = any(b in low for b in BIBLE_WORDS)
 if is_bible:
  biblical_prompt = f"biblical epic movie scene of {p}, ancient Israel, middle eastern people, biblical robes, dramatic holy cinematic lighting, highly detailed, 8k, oil painting"
  safe=urllib.parse.quote_plus(biblical_prompt)
  return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}"

 # 2. FAMOUS, ANIMALS, THINGS = Try REAL first
 real = get_wiki_photo(p)
 if real:
  return real

 # 3. If REAL fails or broken, use AI REALISTIC (so no broken icon)
 fallback_prompt = f"{p}, photorealistic, real photo, highly detailed, 8k, sharp focus, natural light"
 safe=urllib.parse.quote_plus(fallback_prompt)
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}"

if "ch" not in st.session_state: st.session_state.ch=[]
for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else:
  try:
   st.chat_message("assistant").image(m, caption="SI V6.7", use_container_width=True)
  except:
   # If image still fails, show as markdown link so never broken icon
   st.chat_message("assistant").markdown(f"![image]({m})")

q=st.chat_input("Ask ANYTHING - Famous=REAL, Bible=Biblical AI...")
if q:
 ql=q.lower()
 is_img=any(w in ql for w in ["draw","image","picture","photo","generate","create","paint","show me","make a pic","bible"])
 st.session_state.ch.append(("u",q))
 if is_img:
  st.session_state.ch.append(("a",f"V6.7 Creating: {q} 🎨"))
  st.session_state.ch.append(("i",make_image(q)))
 else:
  st.session_state.ch.append(("a",ask(q, st.session_state.ch)))
 st.rerun()
if st.button("Clear Chat ✨"): st.session_state.ch=[]; st.rerun()
