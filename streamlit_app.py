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
st.caption("V8.0 - Exact Answer Engine")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

# FAST DICT FOR GHANA
DICT = {
    "i am hungry": {"twi":"Ɛkɔm de me", "ga":"Gɔmɔ mi", "hausa":"Ina jin yunwa"},
    "i am thirsty": {"twi":"Nsukɔm de me", "ga":"Namɔ mi", "hausa":"Ina jin kishirwa"},
    "go and sleep": {"twi":"Kɔ bɛda", "ga":"Tee ya wɔ", "hausa":"Je ka yi bacci"},
    "go home": {"twi":"Kɔ fie", "ga":"Tee shia", "hausa":"Je gida"},
    "let's go home": {"twi":"Momma yɛnkɔ fie", "ga":"Tee wɔ shia", "hausa":"Mu je gida"},
}

with st.form("chat_form", clear_on_submit=True):
    text = st.text_input("Ask anything", placeholder="Ex: Who is Elon Musk? or Picture of a pilot")
    submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and text.strip():
    q = text.strip()
    low = q.lower()

    last = [m for m in st.session_state.messages if m["role"]=="user"]
    if last and last[-1]["content"] == q:
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})

    # CHECK GHANA DICT FIRST
    handled=False
    for phrase in sorted(DICT.keys(), key=len, reverse=True):
        if phrase in low:
            langs = DICT[phrase]
            out=f"**'{phrase}'** means:\n\n"
            if "twi" in low: out+=f"- **Twi**: **{langs.get('twi','')}** 🇬🇭\n"
            if re.search(r'\bga\b', low): out+=f"- **Ga**: **{langs.get('ga','')}** 🇬🇭\n"
            if "hausa" in low: out+=f"- **Hausa**: **{langs.get('hausa','')}** 🇳🇬\n"
            if out.count("-")==0:
                for k,v in langs.items(): out+=f"- {k.title()}: **{v}**\n"
            st.session_state.messages.append({"role":"assistant","content":out})
            handled=True
            break

    if not handled:
        is_image = ("picture of" in low or low.startswith("draw") or low.startswith("generate image"))
        if any(x in low for x in ["how to say","what is","who is","how many","when","where","why","translate","meaning of"]):
            is_image=False

        if is_image:
            clean = re.sub(r'picture of a|picture of|draw a|draw|generate image of', '', low).strip()
            clean = clean.replace("volture","vulture")
            if not clean: clean="pilot"

            # SAFE EXACT PROMPT
            if "pilot" in clean:
                prompt = "professional airplane pilot wearing full blue flight suit uniform inside airplane cockpit, smiling, SFW, photorealistic, 8k"
            elif "fight" in clean:
                prompt = "two boys boxing training with gloves in boxing ring, sports, safe, photorealistic"
            else:
                prompt = f"{clean}, photorealistic, 8k, accurate anatomy, SFW, modest clothing, professional photo"

            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true&model=flux&safe=true"
            st.session_state.messages.append({"role":"assistant","type":"image","content":url})
        else:
            # EXACT ANSWER ENGINE - BIG MODEL
            try:
                system_prompt = """
You are SI Worldwide Exact AI.
RULES:
1. Give EXACT, direct, factual answers. No empty, no maybe.
2. If translation: Twi Ɛkɔm de me = I am hungry, Ga Gɔmɔ mi, Hausa Ina jin yunwa. Pilita = pilot in Twi.
3. If who/what/when/where: give precise definition, dates, facts.
4. Keep answer short, clear, with bullet points or table if needed.
5. Never say you don't know. Always try to answer exactly.
6. Support Twi, Ga, Hausa, Ewe, German, Hindi, French.
"""
                # Use BEST model for exact answers
                r = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role":"system","content":system_prompt},
                        {"role":"user","content":q}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                ans = r.choices[0].message.content
                if not ans or len(ans.strip())<3:
                    # fallback to smaller model
                    r2 = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role":"user","content":q}],
                        max_tokens=800
                    )
                    ans = r2.choices[0].message.content

                st.session_state.messages.append({"role":"assistant","content":ans})

            except Exception as e:
                st.session_state.messages.append({"role":"assistant","content":f"I tried to answer '{q}' but got error: {e}\n\nTry again - model is llama-3.3-70b."})

    st.rerun()
