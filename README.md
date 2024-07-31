# Subtitle Enhancer

This Streamlit app enhances subtitles by improving their grammatical quality and synchronizing them with audio transcriptions. It uses OpenAI's Whisper model for audio transcription and GPT-4 for grammatical enhancement, allowing you to upload both MP3 and SRT files, process them, and download the improved subtitles.

## Features

- Upload MP3 and SRT files.
- Transcribe audio using OpenAI's Whisper model.
- Enhance subtitle text by synchronizing it with the transcribed audio.
- Improve the grammatical quality of subtitles using GPT-4.
- Download the enhanced subtitles as an SRT file.

## How to Use

1. **Upload Files**: Upload both an MP3 file and an SRT file.
2. **Enter API Key**: Input your OpenAI API key.
3. **Enhance Subtitles**: Click the "Enhance Subtitles" button to start the enhancement process.
4. **Download**: Download the enhanced SRT file once the process is complete.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GaebsApps/subtitle_enhancer.git
   cd subtitle_enhancer

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Running the App

Run the Streamlit app:
  ```bash
  streamlit run streamlit_app.py

## Dependencies

Streamlit
OpenAI
pysrt
tempfile
os
bisect

## License

This project is licensed under the MIT License.
