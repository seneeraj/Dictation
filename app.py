import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from docx import Document
from docx.shared import Pt
import base64
from io import BytesIO
import tempfile
from pydub import AudioSegment

st.set_page_config(page_title="🎙️ Voice Typing App", layout="centered")
st.title("🗣️ Voice Typing — Hindi / English / Hinglish")

lang_option = st.selectbox("Select Language:", ["English", "Hindi", "Hinglish"])
lang_code = {"English": "en-IN", "Hindi": "hi-IN", "Hinglish": "hi-IN"}[lang_option]

st.markdown("### Step 2: 🎤 Click below to Start Recording")
audio_bytes = audio_recorder()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")  # Still useful for preview

    # Convert to wav using pydub
    audio = AudioSegment.from_file(BytesIO(audio_bytes))  # auto-detect format (m4a/wav)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        audio.export(tmp_wav.name, format="wav")
        tmp_path = tmp_wav.name

    # Transcribe
    r = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = r.record(source)
    try:
        text = r.recognize_google(audio_data, language=lang_code)
        st.success("✅ Transcription complete")
    except sr.UnknownValueError:
        text = ""
        st.error("Could not understand audio")

    if text:
        edited = st.text_area("📝 Edit transcription", text, height=200)
        if st.button("💾 Save as Word (.doc)"):
            doc = Document()
            run = doc.add_paragraph().add_run(edited)
            run.font.size = Pt(14)
            if lang_option != "English":
                run.font.name = "Mangal"
            buf = BytesIO()
            doc.save(buf)
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="transcript.doc">📥 Download .doc</a>'
            st.markdown(href, unsafe_allow_html=True)
