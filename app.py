import streamlit as st
import os
import subprocess

def transcribe_video_to_text(video_path, output_txt_path):
    try:
        if os.path.exists(output_txt_path):
            return f\"Skipped (already transcribed): {video_path}\"
        command = [\"whisper\", video_path, \"--model\", \"base\", \"--output_format\", \"txt\"]
        subprocess.run(command, check=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        transcribed_file = base_name + \".txt\"
        if os.path.exists(transcribed_file):
            os.rename(transcribed_file, output_txt_path)
            return f\"Transcription saved to {output_txt_path}\"
        else:
            return f\"Transcription file not found after running Whisper for {video_path}\"
    except subprocess.CalledProcessError as e:
        return f\"Error in transcription: {e}\"

st.title('Video Transcription App')
uploaded_file = st.file_uploader(\"Upload a video file\", type=[\"mp4\", \"mkv\", \"avi\", \"mov\"])

if uploaded_file:
    videos_folder = \"uploads\"
    transcripts_folder = \"transcripts\"
    os.makedirs(videos_folder, exist_ok=True)
    os.makedirs(transcripts_folder, exist_ok=True)

    video_path = os.path.join(videos_folder, uploaded_file.name)
    with open(video_path, \"wb\") as f:
        f.write(uploaded_file.getbuffer())

    output_txt_path = os.path.join(transcripts_folder, os.path.splitext(uploaded_file.name)[0] + \".txt\")

    st.text(\"Transcribing...\")
    result = transcribe_video_to_text(video_path, output_txt_path)
    st.text(result)

    if os.path.exists(output_txt_path):
        with open(output_txt_path, \"r\", encoding=\"utf-8\") as file:
            transcript = file.read()
        st.subheader(\"Transcript:\")
        st.text_area(\"\", transcript, height=300)
