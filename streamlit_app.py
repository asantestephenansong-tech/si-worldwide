import streamlit as st
from groq import Groq
import urllib.parse, re, requests

st.set_page_config(page_title="SI Worldwide", page_icon="🌍", layout="centered")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def get_anyone_photo(query):
    q = query.strip()
    low = q.lower()
    safe_q = low.replace("girls","young women")
    if any(x in low for x in ["nude","naked","sex","porn"]):
        return None, "Cannot provide nude image"

    # --- BIBLICAL FIX ---
    if "abraham" in low and "feet" in low:
        url = "https://image.pollinations.ai/prompt/Biblical scene Abraham washing angels feet with water basin at Mamre oak trees, ancient middle eastern tent, realistic painting?width=800&height=600&nologo=true&seed=101"
        return url, "Abraham washing angels feet - Genesis 18:4"
    if "isaac" in low and ("wood" in low or "moriah" in low):
        url = "https://image.pollinations.ai/prompt/Isaac carrying wood up Mount Moriah with Abraham, ram in thicket thorns, Sodom smoke valley behind, dramatic sunrise, biblical realistic?width=800&height=600&nologo=true&seed=102"
        return url, "Mount Moriah - God will provide Himself"
    if "machpelah" in low or "cave" in low:
        url = "https://image.pollinations.ai/prompt/Abraham buying cave of Machpelah from Ephron Hittites, counting silver shekels at city gate, ancient Canaan?width=800&height=600&nologo=true&seed=103"
        return url, "Cave of Machpelah - Full Price"
    if "sodom" in low:
        url = "https://image.pollinations.ai/prompt/Angels rescuing Lot from burning Sodom fire and brimstone?width=800&height=600&nologo=true&seed=104"
        return url, "Sodom - When Mercy Runs Out"

    try:
        search_api = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(safe_q)}&format=json&srlimit=3"
        r = requests.get(search_api, timeout=6).json()
        results = r.get("query",{}).get("search",[])
        if results:
            title = results[0]["title"]
            page_api = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=600"
            pr = requests.get(page_api, timeout=6).json()
            pages = pr.get("query",{}).get("pages",{})
            for pid in pages:
                if "thumbnail" in pages[pid]:
                    return pages[pid]["thumbnail"]["source"], title
    except:
        pass
    return None, "No image found"

st.title("🌍 SI Worldwide")
st.caption("Evening Class - Biblical AI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "image" in m and m["image"]:
            st.image(m["image"], caption=m.get("cap",""))

if prompt := st.chat_input("Ask - e.g., Picture Abraham washing angels feet"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    img_url, cap = None, ""
    if "picture" in prompt.lower() or "image" in prompt.lower() or "photo" in prompt.lower():
        img_url, cap = get_anyone_photo(prompt)

    try:
        sys_prompt = "You are SI Worldwide Evening Class teacher, explain Bible Genesis with Accra application."
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":sys_prompt},{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=800
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        answer = f"AI error: {e}"

    with st.chat_message("assistant"):
        st.markdown(answer)
        if img_url:
            st.image(img_url, caption=cap)

    msg = {"role":"assistant","content":answer}
    if img_url:
        msg["image"]=img_url
        msg["cap"]=cap
    st.session_state.messages.append(msg)
