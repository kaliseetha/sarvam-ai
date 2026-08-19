import os
import base64
import tempfile

import streamlit as st
from dotenv import load_dotenv
from sarvamai import SarvamAI


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Sarvam Voice AI POC",
    page_icon="🎙️",
    layout="centered",
)


# ---------------------------------------------------------
# Validate API key
# ---------------------------------------------------------

if not SARVAM_API_KEY:
    st.error(
        "SARVAM_API_KEY is not configured. "
        "Please add it to your .env file."
    )
    st.stop()


# ---------------------------------------------------------
# Sarvam client
# ---------------------------------------------------------

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

st.title("🎙️ Sarvam AI Voice Assistant")

st.write(
    "Speak in Tamil or English. "
    "Sarvam will convert your voice to text, "
    "generate an AI answer, and speak the answer back."
)

st.divider()


# ---------------------------------------------------------
# Language selection
# ---------------------------------------------------------

LANGUAGES = {
    "Tamil": "ta-IN",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Auto Detect": "unknown",
}

language_name = st.selectbox(
    "Select input language",
    options=list(LANGUAGES.keys()),
)

language_code = LANGUAGES[language_name]


# ---------------------------------------------------------
# Voice input
# ---------------------------------------------------------

st.subheader("🎤 Step 1 — Ask your question")

audio_file = st.audio_input(
    "Record your question"
)


# ---------------------------------------------------------
# Helper: Speech to Text
# ---------------------------------------------------------

def speech_to_text(audio_bytes, language_code):

    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp_file:

        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name

    try:

        with open(temp_file_path, "rb") as audio:

            response = client.speech_to_text.transcribe(
                file=audio,
                model="saaras:v3",
                language_code=language_code,
                mode="transcribe",
            )

        return response

    finally:

        try:
            os.remove(temp_file_path)
        except OSError:
            pass


# ---------------------------------------------------------
# Helper: LLM
# ---------------------------------------------------------

def generate_answer(question):

    system_prompt = """
You are a helpful educational AI assistant.

Answer the student's question clearly and accurately.

Rules:
- Keep the answer concise.
- Explain difficult concepts simply.
- If the question is related to JEE,
  explain the concept at an appropriate JEE level.
- Use examples where useful.
- Do not invent facts.
"""

    response = client.chat.completions(
        model="sarvam-105b",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0.3,
        max_tokens=500,
        reasoning_effort=None,
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# Helper: Text to Speech
# ---------------------------------------------------------

def text_to_speech(text, language_code):

    # Bulbul supports specific languages.
    # For this POC we use the selected language.

    response = client.text_to_speech.convert(
        text=text,
        model="bulbul:v3",
        language_code=language_code,
        speaker="ratan",
        pace=1.0,
        speech_sample_rate=24000,
    )

    return response


# ---------------------------------------------------------
# Process button
# ---------------------------------------------------------

if audio_file:

    st.audio(
        audio_file,
        format="audio/wav"
    )

    if st.button(
        "🚀 Process Voice",
        type="primary",
        use_container_width=True
    ):

        # -----------------------------------------------
        # Step 1: STT
        # -----------------------------------------------

        with st.spinner(
            "🎤 Converting your voice to text..."
        ):

            try:

                stt_response = speech_to_text(
                    audio_file.getvalue(),
                    language_code
                )

                transcript = stt_response.transcript

            except Exception as e:

                st.error(
                    f"Speech-to-text failed: {str(e)}"
                )

                st.stop()


        # -----------------------------------------------
        # Display transcription
        # -----------------------------------------------

        st.subheader("📝 Your Question")

        st.info(transcript)


        # -----------------------------------------------
        # Step 2: LLM
        # -----------------------------------------------

        with st.spinner(
            "🤖 Generating AI response..."
        ):

            try:

                answer = generate_answer(
                    transcript
                )

            except Exception as e:

                st.error(
                    f"AI response failed: {str(e)}"
                )

                st.stop()


        # -----------------------------------------------
        # Display answer
        # -----------------------------------------------

        st.subheader("🤖 AI Answer")

        st.write(answer)


        # -----------------------------------------------
        # Step 3: TTS
        # -----------------------------------------------

        # Use the same language as input.
        #
        # Auto-detect cannot be directly used as the
        # TTS language code, so we use English as a
        # fallback in this first POC.

        tts_language = language_code

        if tts_language == "unknown":

            detected_language = getattr(
                stt_response,
                "language_code",
                None
            )

            if detected_language:
                tts_language = detected_language
            else:
                tts_language = "en-IN"


        with st.spinner(
            "🔊 Generating voice response..."
        ):

            try:

                tts_response = text_to_speech(
                    answer,
                    tts_language
                )

            except Exception as e:

                st.error(
                    f"Text-to-speech failed: {str(e)}"
                )

                st.stop()


        # -----------------------------------------------
        # Extract audio
        # -----------------------------------------------

        try:

            audio_base64 = tts_response.audios[0]

            audio_bytes = base64.b64decode(
                audio_base64
            )

        except Exception as e:

            st.error(
                f"Unable to decode audio: {str(e)}"
            )

            st.stop()


        # -----------------------------------------------
        # Play response
        # -----------------------------------------------

        st.subheader(
            "🔊 AI Voice Response"
        )

        st.audio(
            audio_bytes,
            format="audio/wav"
        )

        st.success(
            "Voice conversation completed!"
        )