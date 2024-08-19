import tempfile
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

#1  Function to convert text summary to audio
# def text_to_audio(summary_text):
#     tts = gTTS(text=summary_text, lang='en')
#     audio_file = BytesIO()
#     tts.save(audio_file)
#     audio_file.seek(0)  # Move pointer to the start of the file
#     return audio_file



# 2 Function to convert text summary to audio
# def text_to_audio(summary_text):
#     # Save audio to BytesIO object
#     tts = gTTS(text=summary_text, lang='en')
#     audio_file = BytesIO()  # Create a BytesIO object
#     tts.save(audio_file)    # Save the audio content to the BytesIO object
#     audio_file.seek(0)      # Set the pointer to the beginning of the BytesIO object
#     return audio_file

# 3Function to convert text summary to audio
# def text_to_audio(summary):
    """
    This function generates audio from text and returns it as a byte array.

    Args:
        summary_text: The text to convert to audio.

    Returns:
        A byte array containing the audio data.
    """
    # try:
    #     tts = gTTS(text=summary, lang='en')
    #     audio_file = BytesIO()
    #     tts.save(audio_file)
    #     audio_file.seek(0)
    #     return audio_file.getvalue()
    # except Exception as e:
    #     print(f"Error generating audio method: {e}")
    #     return None


def text_to_audio(text):
  try:
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
      tts.save(temp_file.name)
      temp_file.seek(0)
      audio_bytes = temp_file.read()
    return audio_bytes
  except Exception as e:
    print(f"Error generating audio method: {e}")
    return None






# Streamlit UI
st.title("😎 My Content Summarizer: YouTube, Website, or PDF")
name = st.text_input("What's your name?")

# Radio button to select input type
input_type = st.radio(
    "Select an option to summarize:",
    ("YouTube Video", "Website Link", "Upload PDF")
)

if "content" not in st.session_state:
    st.session_state.content = ""

# Extract content based on user selection
if input_type == "YouTube Video":
    youtube_link = st.text_input("Enter YouTube Video Link:")
    st.warning("Ensure Transcript or Captions are on!")
    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

    if st.button("Retrieve and Summarize"):
        st.session_state.content = extract_transcript_details(youtube_link)

elif input_type == "Website Link":
    website_link = st.text_input("Enter Website URL:")
    st.warning("Use small website's link for better performance!")
    if st.button("Retrieve and Summarize"):
        st.session_state.content = extract_website_content(website_link)

elif input_type == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type="pdf")
    if uploaded_file and st.button("Retrieve and Summarize"):
        st.session_state.content = extract_pdf_text(uploaded_file)

#1Generate summary if content is available
# if st.session_state.content:
#     summary = generate_gemini_content(st.session_state.content)
#     st.markdown(f"# Here is your summary, {name}!")
#     st.write(summary)

#     # 2 Convert summary to audio
#     if st.button("Convert Summary to Audio"):
#         try:
#         # Generate audio from summary
#             audio_bytes = text_to_audio(summary)
        
#         # Play audio
#             st.audio(audio_bytes, format="audio/mp3")  # Make sure 'audio/mp3' is used for mp3 format
#         except Exception as e:
#             st.error(f"Error generating audio: {e}")

# 2 Generate summary if content is available
if st.session_state.content:
    summary = generate_gemini_content(st.session_state.content)
    st.markdown(f"# Here is your summary, {name}!")
    st.write(summary)

    if st.button("Convert Summary to Audio"):
        try:
      # Generate audio from summary
            audio_bytes = text_to_audio(summary)
            print(audio_bytes)

      # Play audio
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")  
            else:
                st.error("Error generating audio.") # Make sure 'audio/mp3' is used for mp3 format

        except Exception as e:
            st.error(f"Error generating audio file: {e}")


    # 1 Convert summary to audio
    # if st.button("Convert Summary to Audio"):
    #     try:
    #         audio_bytes = text_to_audio(summary)
    #         st.audio(audio_bytes, format="audio/mp3")  # Or 'audio/wav' if using WAV
    #     except Exception as e:
    #         st.error(f"Error generating audio: {e}")
