import streamlit as st
from groq import Groq
import urllib.parse, re, requests

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_real_photo(query):
    """Get REAL photo from Wikipedia & Wikimedia Commons - worldwide!"""
    # Clean query
    q = query.strip()

    # 1. Try English Wikipedia Page Image (best for people)
    try:
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(q)}&prop=pageimages&format=json&pithumbsize=800&pilicense=any"
        r = requests.get(wiki_url, timeout=6, headers={"User-Agent":"SI-Worldwide/1.0"}).json()
        pages = r.get("query",{}).get("pages",{})
        for p in pages.values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], f"Real Wikipedia photo of {q.title()}"
    except:
        pass

    # 2. Try Wikimedia Commons Search (best for anything: vulture, pilot, car)
    try:
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&srlimit=3&format=json"
        r = requests.get(search_url, timeout=6, headers={"User-Agent":"SI-Worldwide/1.0"}).json()
        results = r.get("query",{}).get("search",[])
        for item in results:
            title = item["title"] # File:John Mahama...
            # Skip logos, maps, icons
            if any(x in title.lower() for x in ["logo","icon","map","flag","svg"]):
                continue
            info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
            r2 = requests.get(info_url, timeout=6).json()
            pages = r2.get("query",{}).get("pages",{})
            for p in pages.values():
                if "imageinfo" in p and p["imageinfo"]:
                    img_url = p["imageinfo"][0]["url"]
                    # Only jpg/png
                    if img_url.lower().endswith((".jpg",".jpeg",".png")):
                        return img_url, f"Real photo: {title.replace('File:','')}"
    except:
        pass

    # 3. Fallback to Unsplash real photos (for anything)
    try:
        # Unsplash source gives REAL photos
        unsplash_url = f"https://source.unsplash.com/800x600/?{urllib.parse.quote(q)}"
        return unsplash_url, f"Real world photo of {q.title()}"
    except:
        pass

    return None, None

st.title("SI Worldwide 🌍")
st.caption("V9.0 - Real Pictures Worldwide")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True, caption=m.get("caption",""))
            if m.get("source"):
                st.caption(f"Source: {m['source']}")
        else:
            st.markdown(m["content"])

st.divider()

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Ask anything", placeholder="Picture of John Mahama, Elon Musk, vulture, Accra, pilot...")
    submitted = st.form_submit_button("Search Real Photo ➤", use_container_width=True)

if submitted and text.strip():
    q = text.strip()
    low = q.lower()

    last = [m for m in st.session_state.messages if m["role"]=="user"]
    if last and last[-1]["content"] == q:
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})

    is_image = any(x in low for x in ["picture of","photo of","image of","draw","show me"])
    # If question words, it's NOT image
    if any(x in low for x in ["what is","who is","can a","meaning","translate","how to say","english word","how many"]):
        is_image=False

    if is_image:
        clean = re.sub(r'picture of a|picture of|photo of|image of|draw a|draw|show me a|show me', '', low).strip()
        clean = clean.replace("volture","vulture").replace("elorn","elon")
        if not clean:
            clean = "world"

        with st.spinner(f"Searching real photo of {clean.title()} worldwide..."):
            real_url, caption = get_real_photo(clean)

        if real_url:
            st.session_state.messages.append({
                "role":"assistant",
                "type":"image",
                "content":real_url,
                "caption": caption,
                "source": "Wikipedia / Wikimedia Commons - Real Photo"
            })
        else:
            # Last resort AI but with safe prompt
            prompt = f"{clean}, professional real photograph, 8k, accurate"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=turbo&safe=true"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url,"caption":f"AI photo of {clean.title()}"})
    else:
        # EXACT ANSWERS
        ans=None
        models = ["llama-3.1-8b-instant","llama3-70b-8192","mixtral-8x7b-32768","gemma2-9b-it","openai/gpt-oss-20b"]
        system = "You are SI Worldwide. Give EXACT, short, factual answers. For translations give Twi, Ga, Hausa."
        for model in models:
            try:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"system","content":system},{"role":"user","content":q}],
                    temperature=0.2, max_tokens=800
                )
                ans = r.choices[0].message.content
                if ans and len(ans.strip())>3:
                    break
            except:
                continue
        st.session_state.messages.append({"role":"assistant","content":ans or "Exact answer not found, try again."})

    st.rerun()
