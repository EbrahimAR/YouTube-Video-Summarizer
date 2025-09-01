# 📺 YouTube Video Summarizer (Whisper + Gemini AI)

A Streamlit-based web app that summarizes YouTube videos into structured reports or notes using:
- **Google Gemini AI** for summarization
- **YouTubeTranscriptApi** for transcript fetching
- **Faster-Whisper** for audio transcription (fallback when no transcript)
- **yt-dlp** for audio downloading
- **ReportLab** for generating PDF reports

---

## ✅ Features
- ✔ Summarizes **entire YouTube videos into structured reports** (Introduction, Main Points, Key Takeaways)
- ✔ Supports **videos without subtitles** using Whisper transcription
- ✔ Handles **long transcripts** with chunking + merging
- ✔ Downloads **PDF notes** with clean formatting
- ✔ Displays **video info and thumbnail**
- ✔ Uses **Streamlit for UI**

---

## 🛠 Tech Stack
- **Python 3.10+** (Recommended)
- **Streamlit** (Frontend UI)
- **Google Generative AI (Gemini)** for summarization
- **Faster-Whisper** for speech-to-text
- **yt-dlp** for audio download
- **YouTubeTranscriptApi** for captions
- **ReportLab** for PDF generation

---

## 📂 Project Structure
    AI-Exam-System/
    ├── main.py
    ├── requirements.txt
    ├── README.md
    ├── LICENSE
    └── .gitignore
    
---

## ⚙️ Installation

### **1. Clone the Repository**
    ```bash
    git clone https://github.com/EbrahimAR/Youtube-Video-Summarizer.git
    cd youtube-video-summarizer
    ```

### **2. Create a virtual environment (recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate     # For Windows
    ```


### **3. Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    
---

## 🔑 Set Your API Key

You need a **Gemini API key** from [Google AI Studio](https://aistudio.google.com/).

Add it as:
- **Environmental Variable:**
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
    (Windows Powershell)
    ```bash
    setx GEMINI_API_KEY "your_api_key_here"
    ```
**OR**
- **Streamlit Secrets:**
    Create `.streamlit/secrets.toml`:
    ```bash
    GEMINI_API_KEY = "your_api_key_here"
    ```

---

## ▶ Usage

### **Launching the App**

  - Run the script:
    ```bash
    streamlit run main.py
    ```


### **📄 Features in Detail**

  - ✅ **Detailed Report** – Creates a structured summary (Introduction, Main Points, Key Takeaways)
  - ✅ **PDF Export** – Save summaries as a PDF
  - ✅ **Whisper Fallback** – Handles videos without captions
  - ✅ **Gemini AI Integration** – For high-quality summarization

---

## 🔮 Future Improvements

- Add **UI option for summary style** (Detailed Report / Bullet Notes)
- Support **multiple languages**
- Add **audio-only mode for podcasts**

---

## 👨‍💻 Author

Ebrahim Abdul Raoof

[LinkedIn](https://www.linkedin.com/in/ebrahim-ar/)

[GitHub](https://github.com/EbrahimAR)

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE]() for details.
#
