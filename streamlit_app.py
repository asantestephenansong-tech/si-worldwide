import streamlit as st
from groq import Groq
import urllib.parse

st.set_page_config(page_title="SI Worldwide", page_icon="🌍")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("SI Worldwide 🌍")
st.caption("V4.9 - Ghana Languages Fixed")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("type") == "image":
            st.image(m["content"], use_container_width=True)
        else:
            st.markdown(m["content"])

st.divider()

audio = st.audio_input("🎤 Voice")
voice_text = None
if audio:
    try:
        t = client.audio.transcriptions.create(
            file=(audio.name, audio.getvalue()),
            model="whisper-large-v3",
            response_format="text"
        )
        voice_text = str(t)
        st.success(voice_text)
    except Exception as e:
        st.error(str(e))

text = st.text_input("Type here", placeholder="Ex: How do you say come in Ga?")
btn = st.button("Send ➤")

final = None
if voice_text:
    final = voice_text
elif btn and text:
    final = text

if final:
    # Fix short G
    fix = final
    low_fix = fix.lower()
    if " in g" in low_fix or low_fix.endswith(" in g") or low_fix.endswith(" in g?"):
        fix = fix.replace(" in G", " in Ga").replace(" in g", " in Ga")

    st.session_state.messages.append({"role":"user","content":fix})

    low = fix.lower()
    is_mean = "what is" in low or "meaning" in low
    is_pic = ("draw" in low or "picture" in low or "photo" in low) and not is_mean

    if is_pic:
        clean = low.replace("i want a picture of","").replace("picture of","").replace("draw","").strip()
        if clean == "":
            clean = fix
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(clean) + "?width=1024&height=1024&nologo=true"
        st.session_state.messages.append({"role":"assistant","type":"image","content":url})
    else:
        try:
            system = """You are SI Worldwide, Ghana AI.
Rules:
- If user asks "How do you say X in G" -> G means Ga language Ghana.
- Twi examples: Come = Bra, How are you = Wo ho te sen, Thank you = Medaase
- Ga examples: Come = Ba, Come in = Ba mli, How are you = Atɛ o nɛ?, Thank you = Oyiwala donu
- Ewe: Come = Va, Hausa: Come = Zo
- Always answer for Ghana languages when asked.
- Keep answer short, friendly."""

            chat = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role":"system","content":system},
                    {"role":"user","content":fix}
                ],
                max_tokens=500
            )
            ans = chat.choices[0].message.content
            st.session_state.messages.append({"role":"assistant","content":ans})
        except Exception as e:
            st.session_state.messages.append({"role":"assistant","content":f"Error: {e}"})

    st.rerun()
