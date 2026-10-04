import streamlit as st
from groq import Groq
import urllib.parse, re

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SI Worldwide 🌍")
st.caption("V8.2 - Real Celebrity Photos")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

TYPO_FIX = {
    "elorn musk": "Elon Musk",
    "elorn": "Elon Musk",
    "elone musk": "Elon Musk",
    "elon": "Elon Musk",
    "volture": "vulture",
}

DICT = {
    "i am hungry": {"twi":"Ɛkɔm de me", "ga":"Gɔmɔ mi", "hausa":"Ina jin yunwa"},
    "can a cockroach live without head": {"answer": "Yes! A cockroach can live up to 1-2 weeks without its head! It breathes through holes in its body (spiracles), not mouth. It dies from thirst, not head loss."},
    "emmanuel": {"answer": "Emmanuel means 'God is with us' - Hebrew Immanuel."},
}

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Ask anything", placeholder="Ex: Picture of Elon Musk")
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and text.strip():
    q = text.strip()
    low = q.lower()

    last = [m for m in st.session_state.messages if m["role"]=="user"]
    if last and last[-1]["content"] == q:
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})

    handled=False
    for phrase in sorted(DICT.keys(), key=len, reverse=True):
        if phrase in low:
            if "answer" in DICT[phrase]:
                st.session_state.messages.append({"role":"assistant","content": DICT[phrase]["answer"]})
            else:
                out="";
                for k,v in DICT[phrase].items(): out+=f"- {k.title()}: **{v}**\n"
                st.session_state.messages.append({"role":"assistant","content":out})
            handled=True
            break

    if not handled:
        is_image = ("picture of" in low or low.startswith("draw") or "photo of" in low)
        if any(x in low for x in ["how to say","what is","who is","can a","meaning of","how many"]):
            is_image=False

        if is_image:
            clean = re.sub(r'picture of a|picture of|photo of|draw a|draw', '', low).strip()
            # FIX TYPO
            for wrong,right in TYPO_FIX.items():
                if wrong in clean.lower():
                    clean = right
                    break

            # SMART PROMPT FOR CELEBRITIES
            if "elon musk" in clean.lower():
                prompt = "Elon Musk portrait, CEO of Tesla and SpaceX, wearing black suit, professional photo, photorealistic, 8k, real person"
            elif "messi" in clean.lower() or "ronaldo" in clean.lower():
                prompt = f"{clean}, football player, professional portrait, photorealistic, 8k"
            elif "pilot" in clean.lower():
                prompt = "professional airplane pilot in full blue flight suit in cockpit, smiling, SFW, photorealistic"
            else:
                prompt = f"{clean}, professional portrait, photorealistic, 8k, accurate, SFW, modest clothing"

            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux&enhance=true&seed=42&safe=true"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            ans=None
            models = ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it", "openai/gpt-oss-20b"]
            system = "Give EXACT factual answer. Short and correct."
            for model in models:
                try:
                    r = client.chat.completions.create(
                        model=model,
                        messages=[{"role":"system","content":system},{"role":"user","content":q}],
                        temperature=0.2,
                        max_tokens=1000
                    )
                    ans = r.choices[0].message.content
                    if ans and len(ans.strip())>5:
                        break
                except:
                    continue
            st.session_state.messages.append({"role":"assistant","content":ans or "Sorry try again"})
    st.rerun()
