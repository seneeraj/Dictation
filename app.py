import streamlit as st
import speech_recognition as sr
from docx import Document
from docx.shared import Pt
from io import BytesIO
import base64
import tempfile

st.set_page_config(page_title="🎙️ Voice Typing (Hindi/English)", layout="centered")
st.title("🗣️ Upload Audio & Get Transcript")

language = st.selectbox("Choose language", ["English", "Hindi", "Hinglish"])
lang_code = {"English": "en-IN", "Hindi": "hi-IN", "Hinglish": "hi-IN"}[language]

audio_file = st.file_uploader("Upload WAV audio file", type=["wav"])

if audio_file is not None:
    st.audio(audio_file, format="audio/wav")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        audio_path = tmp.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language=lang_code)
        st.session_state["transcribed"] = text
        st.success("✅ Transcription complete.")
    except:
        st.error("Could not understand the audio.")

# Editable Text
if "transcribed" in st.session_state:
    edited = st.text_area("📝 Edit transcription", st.session_state["transcribed"], height=200)

    if st.button("💾 Save as Word (.doc)"):
        doc = Document()
        run = doc.add_paragraph().add_run(edited)
        run.font.size = Pt(14)
        if language != "English":
            run.font.name = "Mangal"

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        st.markdown(
            f'<a href="data:application/octet-stream;base64,{b64}" download="transcript.doc">📥 Download .doc</a>',
            unsafe_allow_html=True
        )
