import streamlit as st
import wave
import json
import os
from vosk import Model, KaldiRecognizer
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
import tempfile

@st.cache_resource
def load_model():
    return Model("models/vosk-model-small-hi-0.22")

model = load_model()

def transcribe_audio(wav_path):
    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    results = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result())["text"])

    results.append(json.loads(rec.FinalResult())["text"])
    return " ".join(results)

def save_to_docx(text, output_path):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Mangal'
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Mangal')
    run = doc.add_paragraph().add_run(text)
    run.font.size = Pt(14)
    doc.save(output_path)

# Streamlit UI
st.set_page_config(page_title="🗣️ Hindi Audio Transcriber", layout="centered")
st.title("🎙️ Hindi Audio to Text (.docx) – Vosk")

uploaded_file = st.file_uploader("Upload only .wav file", type=["wav"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    st.info("🔄 Transcribing...")
    try:
        transcript = transcribe_audio(temp_file_path)
        os.remove(temp_file_path)
    except Exception as e:
        st.error(f"❌ Transcription failed: {e}")
        st.stop()

    edited_text = st.text_area("📝 Edit Transcription", value=transcript, height=300)
    filename = st.text_input("📁 Save As (no extension):", value="transcript")

    if st.button("💾 Save .docx"):
        output_path = f"{filename}.docx"
        save_to_docx(edited_text, output_path)
        st.success(f"✅ Saved as: {output_path}")
