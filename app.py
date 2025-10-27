import streamlit as st
import os
import subprocess
import shutil
import time

def transcribe_video_to_text(video_path, output_txt_path):
    try:
        if os.path.exists(output_txt_path):
            return f"Skipped (already transcribed): {video_path}"

        # Log files before transcription
        st.text("Before Whisper runs, directory contents:\n" + str(os.listdir(os.path.dirname(video_path))))

        command = ["whisper", video_path, "--model", "base", "--output_format", "txt"]
        result = subprocess.run(command, capture_output=True, text=True)

        # Log Whisper outputs
        st.text("Whisper stdout:\n" + result.stdout)
        st.text("Whisper stderr:\n" + result.stderr)

        if result.returncode != 0:
            return f"Whisper failed with error code {result.returncode}: {result.stderr}"

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        upload_dir = os.path.dirname(video_path)
        whisper_output_dir = os.path.join(upload_dir, base_name)

        # Wait for output folder or file to appear
        for _ in range(5):
            # Check if output folder exists and has transcript
            if os.path.isdir(whisper_output_dir):
                txt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.txt')]
                if txt_files:
                    transcript_file = os.path.join(whisper_output_dir, txt_files[0])
                    os.rename(transcript_file, output_txt_path)
                    shutil.rmtree(whisper_output_dir)
                    return f"Transcription saved to {output_txt_path}"
            # Check for transcript file directly in current directory
            elif os.path.isfile(base_name + ".txt"):
                os.rename(base_name + ".txt", output_txt_path)
                return f"Transcription saved to {output_txt_path}"

            time.sleep(1)

        # Final debug logs if neither found
        if os.path.isdir(whisper_output_dir):
            files_in_dir = os.listdir(whisper_output_dir)
            st.text(f"Files inside whisper output folder: {files_in_dir}")

        if os.path.isfile(base_name + ".txt"):
            st.text(f"Found transcript file {base_name}.txt in current directory")

        return (f"Whisper output folder {whisper_output_dir} not found and file {base_name}.txt not present "
                "after waiting.")

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
