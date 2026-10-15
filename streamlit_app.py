import streamlit as st, requests, urllib.parse, random, unicodedata, os, datetime
st.set_page_config(page_title="Stephen's Intelligence", page_icon="🌟", layout="centered")
st.markdown("<style>.stApp{background:#000} h1{color:#D4AF37!important;text-align:center}</style>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
 c1,c2,c3=st.columns([1,1.2,1])
 with c2: st.image("logo.png", use_container_width=True)
st.markdown("<h1>STEPHEN'S INTELLIGENCE</h1><p style='text-align:center;color:#D4AF37'>V6.9 ALL BIBLE</p>", unsafe_allow_html=True)

def clean(t):
 try: return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
 except: return t
def get_key():
 try: return str(st.secrets.get("GROQ_API_KEY","")).strip().replace('"','')
 except: return ""
def ask(q,h):
 k=get_key()
 today = datetime.date.today().strftime("%B %Y")
 system_prompt = f"You are Stephen's Intelligence. Today is {today}. Mbappe=Real Madrid since June 2024. Ronaldo=Al Nassr. Messi=Inter Miami. Use 2026 facts. Short answers."
 m=[{"role":"system","content":system_prompt}]
 for r,msg in h[-6:]:
  if r in ["u","a"]: m.append({"role":"user" if r=="u" else "assistant","content":msg})
 m.append({"role":"user","content":clean(q)})
 try:
  r=requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {k}","Content-Type":"application/json"}, json={"model":"openai/gpt-oss-20b","messages":m,"max_tokens":500}, timeout=30)
  return r.json()["choices"][0]["message"]["content"]
 except: return "Try again"

HEADERS = {"User-Agent": "SI-Worldwide/6.9 Ghana"}
# ALL BIBLE CHARACTERS - 150 names!
BIBLE_WORDS = [
 "bible","gospel","disciples","apostle","prophet","pharaoh","israelite","hebrew","golgotha","calvary","resurrection","crucifixion","ark","exodus","genesis","revelation",
 "adam","eve","cain","abel","seth","noah","ham","shem","japheth",
 "abraham","sarah","isaac","ishmael","jacob","esau","rachel","leah","joseph","benjamin","judah",
 "moses","aaron","miriam","pharaoh","joshua","caleb","ruth","naomi","boaz","samuel","saul","david","goliath","jonathan","solomon","sheba","elijah","elisha","isaiah","jeremiah","ezekiel","daniel","shadrach","meshach","abednego","nebuchadnezzar",
 "esther","mordecai","job","jonah","samson","delilah","gideon","deborah","barak","hannah","eli","enoch","lot","rebecca","hagar","potiphar",
 "mary","joseph","jesus","christ","emmanuel","john the baptist","peter","paul","james","john","andrew","thomas","matthew","mark","luke","judas","judas iscariot","mary magdalene","martha","lazarus","zacchaeus","bartimaeus","nicodemus","pontius pilate","pilate","herod","barnabas","timothy","titus","stephen","cornelius","goliath","herod","ananiah"
]

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

 # 1. ALL BIBLE CHARACTERS = AI BIBLICAL MOVIE STYLE
 is_bible = any(b in low for b in BIBLE_WORDS)
 if is_bible:
  safe_p = p.replace("crucified","on the cross at Golgotha").replace("crucifixion","on the cross at Golgotha")
  # Special for cross scene
  if "cross" in low:
   biblical_prompt = f"reverent biblical illustration of {safe_p}, Golgotha hill ancient Jerusalem, holy sunset, biblical robes, reverent not graphic, artistic distant view, oil painting cinematic 8k"
  elif "david" in low and "goliath" in low:
   biblical_prompt = f"epic biblical scene David young shepherd facing giant Goliath Philistine, Valley of Elah ancient Israel, sling in hand, cinematic dramatic lighting, highly detailed 8k"
  elif "moses" in low and "sea" in low:
   biblical_prompt = f"epic biblical scene Moses parting Red Sea, staff raised, Israelites crossing, walls of water, dramatic holy light, cinematic 8k"
  elif "noah" in low:
   biblical_prompt = f"epic biblical scene Noah with Noah's Ark, old bearded man, animals entering ark, flood, ancient world, cinematic 8k"
  elif "daniel" in low and "lion" in low:
   biblical_prompt = f"epic biblical scene Daniel in lions den, peaceful Daniel praying among lions, ancient Babylon, dramatic light, cinematic 8k"
  else:
   biblical_prompt = f"epic biblical movie scene of {safe_p}, ancient Israel, middle eastern people with authentic biblical robes and sandals, dramatic holy cinematic lighting, reverent, highly detailed, oil painting, 8k, no modern clothes"

  safe=urllib.parse.quote_plus(biblical_prompt)
  return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}&negative=soccer,football,jersey,modern,car"

 # 2. FAMOUS, ANIMALS, THINGS = REAL Wikipedia
 real = get_wiki_photo(p)
 if real: return real

 # 3. Fallback AI realistic
 safe=urllib.parse.quote_plus(f"{p}, photorealistic, real photo, highly detailed, 8k")
 return f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&nologo=true&model=turbo&seed={random.randint(1,99999999)}"

if "ch" not in st.session_state: st.session_state.ch=[]
for r,m in st.session_state.ch:
 if r=="u": st.chat_message("user").write(m)
 elif r=="a": st.chat_message("assistant").write(m)
 else:
  try: st.chat_message("assistant").image(m, caption="SI V6.9")
  except: st.chat_message("assistant").markdown(f"![image]({m})")

q=st.chat_input("Famous=REAL, ALL Bible=AI Movie...")
if q:
 ql=q.lower()
 is_img=any(w in ql for w in ["draw","image","picture","photo","generate","create","paint","show me","make a pic","bible"])
 st.session_state.ch.append(("u",q))
 if is_img:
  st.session_state.ch.append(("a",f"V6.9 Creating: {q} 🎨"))
  st.session_state.ch.append(("i",make_image(q)))
 else:
  st.session_state.ch.append(("a",ask(q, st.session_state.ch)))
 st.rerun()
if st.button("Clear Chat ✨"): st.session_state.ch=[]; st.rerun()
