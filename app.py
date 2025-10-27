import streamlit as st
import os
import subprocess
import shutil
import time
import re

def remove_timestamps(text):
    # Remove timestamps in format [00:00.000 --> 00:01.160]
    return re.sub(r"\[[0-9:.]+ --> [0-9:.]+\]\s*", "", text)

def transcribe_video_to_text(video_path, output_txt_path):
    if os.path.exists(output_txt_path):
        return None  # Skip if already transcribed

    command = ["whisper", video_path, "--model", "base", "--output_format", "txt"]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        st.error(f"Whisper process failed: {result.stderr}")
        return None

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    upload_dir = os.path.dirname(video_path)
    whisper_output_dir = os.path.join(upload_dir, base_name)

    for _ in range(5):
        if os.path.isdir(whisper_output_dir):
            txt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.txt')]
            if txt_files:
                transcript_file = os.path.join(whisper_output_dir, txt_files[0])
                shutil.move(transcript_file, output_txt_path)
                shutil.rmtree(whisper_output_dir)
                return output_txt_path
        elif os.path.isfile(base_name + ".txt"):
            shutil.move(base_name + ".txt", output_txt_path)
            return output_txt_path
        time.sleep(1)
    return None

st.title("Simple Video Transcription")

uploaded_file = st.file_uploader("Upload a video file (mp4, mkv, avi, mov)", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file:
    videos_folder = "uploads"
    transcripts_folder = "transcripts"
    os.makedirs(videos_folder, exist_ok=True)
    os.makedirs(transcripts_folder, exist_ok=True)

    video_path = os.path.join(videos_folder, uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    transcript_path = os.path.join(transcripts_folder, os.path.splitext(uploaded_file.name)[0] + ".txt")
    transcribed_file = transcribe_video_to_text(video_path, transcript_path)

    if transcribed_file and os.path.exists(transcribed_file):
        with open(transcribed_file, "r", encoding="utf-8") as f:
            full_transcript = f.read()

        st.subheader("Transcript with Timestamps")
        st.text_area("", full_transcript, height=300, key="transcript_with_timestamps")

        st.subheader("Transcript without Timestamps")
        text_only = remove_timestamps(full_transcript)
        st.text_area("", text_only, height=300, key="transcript_without_timestamps")

        st.download_button(
            "Download with timestamps",
            full_transcript,
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_with_timestamps.txt",
        )
        st.download_button(
            "Download without timestamps",
            text_only,
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_plain.txt",
        )
    else:
        st.info("Transcription in progress or failed. Please try again.")
