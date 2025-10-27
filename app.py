import streamlit as st
import os
import subprocess
import glob
import shutil
import time

def transcribe_video_to_text(video_path, output_txt_path):
    try:
        if os.path.exists(output_txt_path):
            return f"Skipped (already transcribed): {video_path}"

        # Log files before running Whisper
        st.text("Before Whisper runs, directory contents:\n" + str(os.listdir(os.path.dirname(video_path))))

        command = ["whisper", video_path, "--model", "base", "--output_format", "txt"]
        result = subprocess.run(command, capture_output=True, text=True)

        # Log Whisper output info
        st.text("Whisper stdout:\n" + result.stdout)
        st.text("Whisper stderr:\n" + result.stderr)

        if result.returncode != 0:
            return f"Whisper failed with error code {result.returncode}: {result.stderr}"

        # Log files after running Whisper
        st.text("After Whisper runs, directory contents:\n" + str(os.listdir(os.path.dirname(video_path))))

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        whisper_output_dir = os.path.join(os.path.dirname(video_path), base_name)

        # Wait up to 5 seconds for output folder to appear
        for _ in range(5):
            if os.path.isdir(whisper_output_dir):
                break
            time.sleep(1)

        if not os.path.isdir(whisper_output_dir):
            return f"Whisper output folder {whisper_output_dir} not found after waiting.\nCurrent directory: {os.listdir()}\nUploads folder: {os.listdir(os.path.dirname(video_path))}"

        # Log output folder contents
        files_in_output = os.listdir(whisper_output_dir)
        st.text(f"Files inside Whisper output folder: {files_in_output}")

        txt_files = [f for f in files_in_output if f.endswith('.txt')]
        if txt_files:
            transcript_file = os.path.join(whisper_output_dir, txt_files[0])
            os.rename(transcript_file, output_txt_path)
            shutil.rmtree(whisper_output_dir)
            return f"Transcription saved to {output_txt_path}"
        else:
            return f"No transcription .txt file found in {whisper_output_dir}"

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
        with open(output_txt_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        st.subheader("Transcript:")
        st.text_area("", transcript, height=300)
