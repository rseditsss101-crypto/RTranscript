import streamlit as st
import os
import subprocess
import glob
import shutil

def transcribe_video_to_text(video_path, output_txt_path):
    try:
        if os.path.exists(output_txt_path):
            return f"Skipped (already transcribed): {video_path}"

        command = ["whisper", video_path, "--model", "base", "--output_format", "txt"]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Whisper failed with error: {result.stderr}"

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        whisper_output_dir = os.path.join(os.path.dirname(video_path), base_name)

        if os.path.isdir(whisper_output_dir):
            txt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.txt')]
            if txt_files:
                os.rename(os.path.join(whisper_output_dir, txt_files[0]), output_txt_path)
                shutil.rmtree(whisper_output_dir)
                return f"Transcription saved to {output_txt_path}"
            else:
                return f"No .txt file found in {whisper_output_dir}"
        else:
            return f"Whisper output folder {whisper_output_dir} not found."
    except Exception as e:
        return f"Error during transcription: {e}"

st.title('Video Transcription App')

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file:
    videos_folder = "uploads"
    transcripts_folder = "transcripts"

    os.makedirs(videos_folder, exist_ok=True)
    os.makedirs(transcripts_folder, exist_ok=True)

    video_path = os.path.join(videos_folder, uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    output_txt_path = os.path.join(transcripts_folder, os.path.splitext(uploaded_file.name)[0] + ".txt")

    st.text("Transcribing...")
    result = transcribe_video_to_text(video_path, output_txt_path)
    st.text(result)

    if os.path.exists(output_txt_path):
        with open(output_txt_path, "r", encoding="utf-8") as file:
            transcript = file.read()
        st.subheader("Transcript:")
        st.text_area("", transcript, height=300)
