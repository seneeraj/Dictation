import streamlit as st
import speech_recognition as sr
from docx import Document
from docx.shared import Pt
from io import BytesIO
from pydub import AudioSegment
import tempfile

st.title("📝 AI Stenographer – Hindi / English / Hinglish")

lang = st.selectbox("Select Language:", ["English", "Hindi", "Hinglish"])
lang_code = {"English": "en-IN", "Hindi": "hi-IN", "Hinglish": "hi-IN"}[lang]

uploaded = st.file_uploader("Upload your recorded audio file (WAV, MP3 or M4A):", type=["wav","mp3","m4a"])
if uploaded:
    audio = AudioSegment.from_file(uploaded)
    wav_io = BytesIO()
    audio.export(wav_io, format='wav')
    wav_io.seek(0)
    st.audio(wav_io, format="audio/wav")

    r = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        aud = r.record(source)
        try:
            text = r.recognize_google(aud, language=lang_code)
            st.success("✅ Transcription complete")
        except:
            st.error("Transcription failed")
            text = ""

    edited = st.text_area("Edit Transcript:", text, height=300)
    if st.button("💾 Save as .docx"):
        doc = Document()
        run = doc.add_paragraph().add_run(edited)
        run.font.size = Pt(14)
        if lang in ["Hindi", "Hinglish"]:
            run.font.name = "Mangal"
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button("📄 Download .docx", buf.getvalue(), file_name="transcript.docx")
