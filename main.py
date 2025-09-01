import os
import streamlit as st
import google.generativeai as genai
from faster_whisper import WhisperModel
import yt_dlp
import tempfile
import textwrap
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO

# ------------------ Configuration ------------------

# Load API key from Streamlit secrets or environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
if not GEMINI_API_KEY:
    st.error("❌ Gemini API key not found. Please set it in .streamlit/secrets.toml or as an environment variable.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Load Whisper model
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")  # Options: tiny, base, small, medium, large

# ------------------ Helper Functions ------------------

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        return parse_qs(urlparse(url).query).get("v", [None])[0]
    return None

def get_transcript(video_id):
    """Fetch transcript using YouTubeTranscriptApi."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([entry['text'] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        st.info("Transcript not available from YouTube. Switching to Whisper...")
        return None

def download_audio_and_metadata(video_url):
    """Download audio and metadata from YouTube using yt-dlp."""
    temp_dir = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        audio_path = os.path.join(temp_dir, f"{info['id']}.mp3")

    metadata = {
        'title': info.get('title', 'Untitled Video'),
        'channel': info.get('uploader', 'Unknown'),
        'thumbnail': info.get('thumbnail'),
        'description': info.get('description', '')[:300],
        'audio_path': audio_path
    }
    return metadata

def transcribe_audio(audio_path):
    """Transcribe audio using faster-whisper."""
    segments, info = whisper_model.transcribe(audio_path)
    return " ".join([segment.text for segment in segments])

def summarize_text(text, chunk_size=2000):
    """Generate a single, cohesive report for the entire transcript.
    If transcript is too long, summarize chunks first and then combine them.
    """
    if len(text) <= chunk_size:
        # Direct summarization for short transcripts
        prompt = f"""
        Summarize the following transcript into a single well-structured report for the entire video:

        - Combine all details into ONE report.
        - Do NOT include timestamps.
        - Use sections: Introduction, Main Points (with subheadings), and Key Takeaways.
        - Make it concise, clear, and professional for note-taking or study purposes.

        Transcript:
        {text}
        """
        try:
            response = model.generate_content(prompt)
            return f"### Video Summary Report\n\n{response.text.strip()}"
        except Exception as e:
            return f"❌ Error generating summary: {e}"
    else:
        # Chunked approach for long transcripts
        chunks = textwrap.wrap(text, width=chunk_size, break_long_words=False)
        chunk_summaries = []

        for i, chunk in enumerate(chunks):
            prompt = f"""
            Summarize this part of the transcript into short, clear bullet points (max 5):
            {chunk}
            """
            try:
                response = model.generate_content(prompt)
                chunk_summaries.append(response.text.strip())
            except:
                chunk_summaries.append("Error summarizing this chunk.")

        combined_notes = "\n".join(chunk_summaries)
        final_prompt = f"""
        Combine the following notes into a single well-structured report:
        - Sections: Introduction, Main Points, Key Takeaways
        - Remove repetition
        - Do NOT include timestamps

        Notes:
        {combined_notes}
        """

        try:
            response = model.generate_content(final_prompt)
            return f"### Video Summary Report\n\n{response.text.strip()}"
        except Exception as e:
            return f"❌ Error combining summaries: {e}"

def save_pdf(title, summary_text, filename):
    """Save summary to a PDF file."""
    pdf_path = os.path.join(tempfile.gettempdir(), filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, title)
    c.setFont("Helvetica", 10)
    y = height - 70

    for line in summary_text.split('\n'):
        wrapped_lines = textwrap.wrap(line, 100)
        for wline in wrapped_lines:
            c.drawString(50, y, wline)
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50

    c.save()
    return pdf_path

def display_thumbnail(thumbnail_url):
    try:
        response = requests.get(thumbnail_url)
        img = Image.open(BytesIO(response.content))
        st.image(img, caption="Video Thumbnail", width='content')
    except:
        st.warning("Could not load thumbnail.")

# ------------------ Streamlit App ------------------

st.set_page_config(page_title="YouTube Summarizer", layout="wide")
st.title("📺 YouTube Video Summarizer (Whisper + Gemini AI)")

video_url = st.text_input("Paste a YouTube video URL:")

if st.button("Summarize Video"):
    if not video_url:
        st.error("Please enter a valid YouTube video URL.")
    else:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("Could not extract video ID.")
        else:
            with st.spinner("Fetching transcript or audio..."):
                transcript = get_transcript(video_id)

            if transcript:
                metadata = {
                    'title': f"YouTube Video {video_id}",
                    'channel': "Unknown",
                    'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    'description': ""
                }
            else:
                st.warning("No transcript found. Using Whisper...")
                metadata = download_audio_and_metadata(video_url)
                transcript = transcribe_audio(metadata['audio_path'])

            st.subheader("📌 Video Info")
            st.markdown(f"**Title:** {metadata['title']}")
            st.markdown(f"**Channel:** {metadata.get('channel', 'N/A')}")
            st.markdown(f"**Description:** {metadata.get('description', '')}")
            display_thumbnail(metadata.get('thumbnail'))

            with st.spinner("Summarizing content..."):
                summary = summarize_text(transcript)

            st.subheader("📝 AI Summary")
            st.markdown(summary)

            pdf_path = save_pdf(metadata['title'], summary, f"{video_id}_summary.pdf")
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download PDF Notes", f, file_name=f"{metadata['title']}_summary.pdf", mime="application/pdf")
