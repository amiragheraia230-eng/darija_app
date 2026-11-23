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

try:
    key = st.secrets["GEMINI_API_KEY"]
except Exception:
    key = st.text_input("Gemini API key", type="password")

text = st.text_area("Text (Darija, Amazigh, or any language)")
recorded = st.audio_input("Or record your voice")
uploaded = st.file_uploader(
    "Or upload a voice recording", type=["ogg", "mp3", "wav", "m4a"]
)
audio = recorded or uploaded
target = st.selectbox("Translate to", list(LANG.keys()))
speak = st.checkbox("Read the translation aloud")

if st.button("Translate") and key and (text or audio):
    start = time.time()
    client = genai.Client(api_key=key)
    instruction = (
        f"Translate into {target}. The speech or text may be "
        "Algerian Darija or Amazigh. Do not explain anything. "
        "Reply in exactly this format:\n"
        "TRANSCRIPT: <what was said or written>\n"
        "TRANSLATION: <the translation only>"
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
        model="gemini-3.5-flash-lite", contents=contents
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
