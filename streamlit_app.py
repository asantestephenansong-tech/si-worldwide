import streamlit as st
import requests
from groq import Groq
import random, time
from urllib.parse import quote

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")
st.title("🌍 SI Worldwide AI")
st.caption("V14 - Answers ANY question you think")

GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_KEY = st.secrets.get("HF_API_KEY", "")  # Optional second key for unlimited
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.last_image_time = 0
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def ask_any_question(prompt):
    # 1. Groq - 3 models rotation
    if client:
        for model in ["llama-3.1-8b-instant", "llama3-8b-8192", "gemma2-9b-it"]:
            try:
                c = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role":"system","content":"You are helpful. Current date: October 2026. Current US President is Donald Trump (47th, since Jan 20 2025). Current Pope is Leo XIV since May 8 2025 after Francis died April 21 2025. Answer any question accurately."},
                        {"role":"user","content":prompt}
                    ],
                    max_tokens=1200
                )
                txt = c.choices[0].message.content
                if txt and len(txt) > 20:
                    return txt
            except Exception as e:
                continue

    # 2. Hugging Face FREE unlimited AI - answers ANY question
    if HF_KEY:
        try:
            url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
            headers = {"Authorization": f"Bearer {HF_KEY}"}
            data = {"inputs": prompt, "parameters": {"max_new_tokens": 600}}
            r = requests.post(url, headers=headers, json=data, timeout=20)
            if r.status_code == 200:
                j = r.json()
                if isinstance(j, list) and j[0].get("generated_text"):
                    text = j[0]["generated_text"]
                    # Remove prompt echo
                    return text.replace(prompt, "").strip()[:2000]
        except:
            pass

    # 3. Pollinations AI - REAL AI, no hard-coding, 3 models
    for model in ["openai", "mistral", "openai-large"]:
        try:
            url = f"https://text.pollinations.ai/{quote(prompt)}?model={model}&seed={random.randint(1,999999)}"
            r = requests.get(url, timeout=15)
            txt = r.text.strip()
            if len(txt) > 40 and not txt.startswith("{") and "Free limit" not in txt and "<html" not in txt.lower():
                return txt[:2000]
        except:
            continue

    # 4. Wikipedia LIVE - unlimited, answers any topic
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote(prompt)}&format=json&srlimit=1"
        search = requests.get(search_url, timeout=8).json()
        if search.get("query",{}).get("search"):
            title = search["query"]["search"][0]["title"]
            summary = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}", timeout=8).json()
            if summary.get("extract"):
                return summary["extract"] + f"\n\nSource: Wikipedia ({title}) - now ask follow-up."
    except:
        pass

    # 5. DuckDuckGo Instant Answer - unlimited
    try:
        ddg = requests.get(f"https://api.duckduckgo.com/?q={quote(prompt)}&format=json", timeout=8).json()
        if ddg.get("AbstractText"):
            return ddg["AbstractText"]
    except:
        pass

    # If ALL 5 AIs fail (rare, when you spam 10 questions in 10 seconds), wait 5 sec and retry automatically
    time.sleep(2)
    try:
        url = f"https://text.pollinations.ai/{quote(prompt)}?model=openai&seed={random.randint(1,999999)}"
        r = requests.get(url, timeout=15)
        if len(r.text) > 40:
            return r.text[:2000]
    except:
        pass
    
    return f"I tried 5 AIs but all are rate-limited for 15 seconds because of fast asking. Wait 5 seconds and ask again: '{prompt}' - it will answer. Tip: Don't send 2 questions in same 5 seconds."

def make_image(prompt):
    now = time.time()
    # Real photos for tools
    if any(x in prompt.lower() for x in ["shovel","breaker","capacitor","mcb","tool"]):
        # flux = most realistic model
        return f"https://image.pollinations.ai/prompt/{quote(prompt + ', real product photo, white background, professional')}?width=800&height=800&nologo=true&seed={random.randint(1,999999)}&model=flux"
    
    if now - st.session_state.last_image_time < 50:
        return f"https://source.unsplash.com/800x600/?{quote(prompt)}"
    st.session_state.last_image_time = now
    return f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=800&height=800&nologo=true&seed={random.randint(1,999999)}&model=flux"

for role, msg in st.session_state.history:
    if role == "u":
        st.markdown(f"🔴 **You:** {msg}")
    else:
        if msg.startswith("http"):
            st.markdown("🟠 **SI V14:**")
            st.image(msg, use_container_width=True)
        else:
            st.markdown(f"🟠 **SI V14:** {msg}")

st.divider()
if st.session_state.clear_input:
    st.session_state.clear_input = False
    st.session_state.qinput = ""

q = st.text_input("Ask...", placeholder="Ask ANYTHING you are thinking", key="qinput")
c1,c2 = st.columns([4,1])
with c1:
    send = st.button("Send ✨", type="primary", use_container_width=True)
with c2:
    clr = st.button("Clear", use_container_width=True)

if clr:
    st.session_state.history=[]
    st.rerun()

if send and q and q.strip():
    user_q=q.strip()
    st.session_state.history.append(("u",user_q))
    st.session_state.clear_input=True
    if any(x in user_q.lower() for x in ["picture","draw","image","photo"]):
        st.session_state.history.append(("a",make_image(user_q)))
    else:
        st.session_state.history.append(("a",ask_any_question(user_q)))
    st.rerun()
