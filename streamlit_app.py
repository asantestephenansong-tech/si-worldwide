import streamlit as st, requests, random, time
from groq import Groq
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="SI Worldwide V16", layout="wide")
groq_key = st.secrets.get("GROQ_API_KEY")
poll_key = st.secrets.get("POLLINATIONS_API_KEY","")
client = Groq(api_key=groq_key)

st.title("🌍 SI Worldwide V16")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type")=="image": st.image(m["content"])
        else: st.markdown(m["content"])

prompt = st.chat_input("Ask anything...")
if prompt:
    st.session_state.messages.append({"role":"user","type":"text","content":prompt})
    with st.chat_message("user"): st.markdown(prompt)

    is_img = any(k in prompt.lower() for k in ["picture","image","photo","draw","shovel"])
    
    with st.chat_message("assistant"):
        if is_img:
            safe = " ".join(prompt.lower().replace("picture of a","").replace("picture of","").split())
            enc = requests.utils.quote(safe)
            token = f"&token={poll_key}" if poll_key else ""
            url = f"https://image.pollinations.ai/prompt/{enc}?model=turbo&width=1024&height=1024&seed={random.randint(1,999999)}&nologo=true{token}"
            
            # Try 3 times if limit
            for attempt in range(3):
                try:
                    r = requests.get(url, timeout=20)
                    # If it's the yellow limit image, it's small (<50kb) - retry
                    if len(r.content) < 80000 and attempt < 2:
                        st.warning(f"Free service full - retrying {attempt+1}/3 in 3s... Add POLLINATIONS_API_KEY for unlimited")
                        time.sleep(3)
                        continue
                    st.image(r.content, caption=f"AI illustration: {safe}")
                    st.caption("AI illustration, not real photo")
                    st.session_state.messages.append({"role":"assistant","type":"image","content":r.content})
                    break
                except Exception as e:
                    st.error(f"Trying again... {e}")
                    time.sleep(2)
        else:
            hist = [{"role":"system","content":"You are SI Worldwide V16 by Stephen Asante"}]
            for mm in st.session_state.messages[-6:]:
                if mm.get("type")!="image": hist.append({"role": mm["role"], "content": mm["content"]})
            try:
                comp = client.chat.completions.create(model="openai/gpt-oss-20b", messages=hist, max_tokens=800)
                ans = comp.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","type":"text","content":ans})
            except Exception as e:
                st.error(f"Groq: {e}")
