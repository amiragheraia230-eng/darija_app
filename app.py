import io
import time
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS

LANG = {
    "English": "en", "French": "fr", "Spanish": "es",
    "Chinese": "zh-CN", "Standard Arabic": "ar",
    "Egyptian Arabic": "ar", "Algerian Darija": "ar",
}

st.title("Darija Translator")

if not st.user.is_logged_in:
    st.write("Please sign in to use the translator.")
    st.button("Sign in with Google", on_click=st.login)
    st.stop()

st.write(f"Hello, {st.user.name}")
st.button("Sign out", on_click=st.logout)

try:
    key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("The app is not configured yet.")
    st.stop()

text = st.text_area("Text (Darija, Amazigh, or any language)")
recorded = st.audio_input("Or record your voice")
uploaded = st.file_uploader(
    "Or upload a voice recording", type=["ogg", "mp3", "wav", "m4a"]
)
audio = recorded or uploaded
target = st.selectbox("Translate to", list(LANG.keys()))
speak = st.checkbox("Read the translation aloud")

if st.button("Translate") and (text or audio):
    start = time.time()
    client = genai.Client(api_key=key)
    instruction = (
        "The speech or text may be Algerian Darija or Amazigh. "
        f"Translate it into {target}. The TRANSLATION line must be "
        f"written in {target} only, never in English unless the "
        "target is English. Do not explain anything. "
        "Reply in exactly this format:\n"
        "TRANSCRIPT: <what was said or written>\n"
        f"TRANSLATION: <the translation in {target}>"
    )
    if audio:
        contents = [
            instruction,
            types.Part.from_bytes(
                data=audio.getvalue(),
                mime_type=audio.type or "audio/wav",
            ),
        ]
    else:
        contents = f"{instruction}\n\n{text}"
    reply = client.models.generate_content(
        model="gemini-3.5-flash", contents=contents
    )
    answer = reply.text
    st.write(answer)
    st.caption(f"Translated in {time.time() - start:.1f} seconds")

    if speak:
        spoken = answer.split("TRANSLATION:")[-1].strip()
        try:
            buf = io.BytesIO()
            gTTS(spoken, lang=LANG[target]).write_to_fp(buf)
            st.audio(buf.getvalue(), format="audio/mp3")
        except Exception:
            st.warning("Could not create the voice.")
