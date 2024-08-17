import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
from PyPDF2 import PdfReader
from gtts import gTTS
import os
import google.generativeai as genai
import requests
from io import BytesIO

load_dotenv()  # Load environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You will summarize the provided content in less than 150 words. Here's the content: """

# Function to extract transcript from YouTube
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

# Function to extract text from a PDF
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to summarize text using Gemini API
def generate_gemini_content(content_text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + content_text)
    return response.text

# Function to extract content from a website
def extract_website_content(website_url):
    try:
        response = requests.get(website_url)
        return response.text
    except Exception as e:
        raise e

# Function to convert text summary to audio
def text_to_audio(summary_text):
    tts = gTTS(text=summary_text, lang='en')
    return tts

# Streamlit UI
st.title("Summarizer: YouTube, Website, or PDF")
name = st.text_input("What's your name?")

# Radio button to select input type
input_type = st.radio(
    "Select an option to summarize:",
    ("YouTube Video", "Website Link", "Upload PDF")
)

content = ""
if input_type == "YouTube Video":
    youtube_link = st.text_input("Enter YouTube Video Link:")
    if youtube_link:
        st.warning("Ensure Transcript or Captions are on!")
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    if st.button("Retrieve and Summarize"):
        content = extract_transcript_details(youtube_link)

elif input_type == "Website Link":
    website_link = st.text_input("Enter Website URL:")
    st.warning("Use small website's link for better performance!")
    if st.button("Retrieve and Summarize"):
        content = extract_website_content(website_link)

elif input_type == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
    if uploaded_file and st.button("Retrieve and Summarize"):
        content = extract_pdf_text(uploaded_file)

# Generate summary if content is available
if content:
    summary = generate_gemini_content(content)
    st.markdown(f"# Here is your summary, {name}!")
    st.write(summary)

    # # Convert summary to audio
    # if st.button("Convert Summary to Audio"):
    #     audio = text_to_audio(summary)
    #     audio_bytes = BytesIO()
    #     audio.write_to_fp(audio_bytes)
    #     st.audio(audio_bytes.getvalue(), format="audio/mp3")


    # Convert summary to audio
    if st.button("Convert Summary to Audio"):
        try:
            audio = text_to_audio(summary)
            audio_bytes = BytesIO()
            audio.write_to_fp(audio_bytes)
        
        # Optionally convert to WAV for wider compatibility
        # from io import BytesIO
        # import wave
        # wav_file = BytesIO()
        # wave_writer = wave.open(wav_file, 'wb')
        # wave_writer.setnchannels(1)  # Assuming mono audio
        # wave_writer.setsampwidth(2)  # 16-bit audio
        # wave_writer.setframerate(44100)  # 44.1 kHz sample rate
        # wave_writer.writeframes(audio_bytes.getvalue())
        # wave_writer.close()
        # audio_bytes = wav_file

            st.audio(audio_bytes.getvalue(), format="audio/mpeg")  # Or 'audio/wav' if using WAV
        except Exception as e:
            st.error(f"Error generating audio: {e}")