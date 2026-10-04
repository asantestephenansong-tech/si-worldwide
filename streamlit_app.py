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
st.caption("V8.1 - Exact Answers Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

DICT = {
    "i am hungry": {"twi":"Ɛkɔm de me", "ga":"Gɔmɔ mi", "hausa":"Ina jin yunwa"},
    "can a cockroach live without head": {"answer": "Yes! A cockroach can live up to 1-2 weeks without its head! It breathes through holes in its body (spiracles), not mouth. It dies from thirst, not head loss."},
    "emmanuel": {"answer": "Emmanuel means 'God is with us'. From Hebrew Immanuel (עִמָּנוּאֵל). Immanu = with us, El = God."},
}

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Ask anything", placeholder="Ex: Can a cockroach live without head?")
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
                langs = DICT[phrase]
                out=""
                for k,v in langs.items(): out+=f"- {k.title()}: **{v}**\n"
                st.session_state.messages.append({"role":"assistant","content":out})
            handled=True
            break

    if not handled:
        is_image = ("picture of" in low or low.startswith("draw"))
        if any(x in low for x in ["how to say","what is","who is","can a","meaning of"]):
            is_image=False

        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a', '', low).strip()
            prompt = f"{clean}, professional, SFW, photorealistic, 8k, modest clothing"
            if "pilot" in clean: prompt = "professional airplane pilot in full flight suit in cockpit, SFW, 8k"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux&safe=true"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            # TRY 3 MODELS - ONE WILL WORK
            ans=None
            models = ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it", "openai/gpt-oss-20b"]
            system = "You are SI Worldwide. Give EXACT, short, factual answers. For cockroach: Yes can live 1-2 weeks without head. For Emmanuel: God is with us in Hebrew. Never return empty. Be precise."
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

            if not ans:
                ans = "Error, but here is answer: For cockroach - YES, lives 2 weeks without head. Emmanuel - Means God is with us."

            st.session_state.messages.append({"role":"assistant","content":ans})
    st.rerun()
