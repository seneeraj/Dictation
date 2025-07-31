import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from docx import Document
from docx.shared import Pt
import base64
from io import BytesIO
import tempfile

st.set_page_config(page_title="🎙️ Voice Typing App", layout="centered")
st.title("🗣️ Voice Typing — Hindi / English / Hinglish")

# Step 1: Language selection
lang_option = st.selectbox("Select Language:", ["English", "Hindi", "Hinglish"])
lang_code = {"English": "en-IN", "Hindi": "hi-IN", "Hinglish": "hi-IN"}[lang_option]

# Step 2: Choose input method
input_method = st.radio("Choose Input Method:", ["🎤 Record Audio", "📁 Upload .wav File"])

audio_bytes = None
if input_method == "🎤 Record Audio":
    st.markdown("### Step 3: Click below to Start Recording")
    audio_bytes = audio_recorder()
elif input_method == "📁 Upload .wav File":
    uploaded_file = st.file_uploader("Upload your audio (.wav only)", type=["wav"])
    if uploaded_file:
        audio_bytes = uploaded_file.read()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    r = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = r.record(source)
    try:
        text = r.recognize_google(audio_data, language=lang_code)
        st.success("✅ Transcription complete")
    except sr.UnknownValueError:
        text = ""
        st.error("❌ Could not understand the audio")

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
