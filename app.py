import os
import base64
import tempfile

import streamlit as st
from dotenv import load_dotenv
from sarvamai import SarvamAI


# =========================================================
# Configuration
# =========================================================

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="Sarvam Voice AI | Kalidasan Seetharaman",
    page_icon="🎙️",
    layout="centered",
)

# =========================================================
# Validate API Key
# =========================================================

if not SARVAM_API_KEY:

    st.error(
        "SARVAM_API_KEY is not configured. "
        "Please add it to your .env file."
    )

    st.stop()


# =========================================================
# Sarvam Client
# =========================================================

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


# =========================================================
# UI Header
# =========================================================

st.title("🎙️ Sarvam AI Voice Assistant")
st.caption("Created by Kalidasan Seetharaman")

st.write(
    "Speak in Tamil or English. "
    "Sarvam converts your voice to text, "
    "generates an AI response, and speaks "
    "the response back to you."
)

st.divider()


# =========================================================
# Language Selection
# =========================================================

LANGUAGES = {
    "Tamil": "ta-IN",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Auto Detect": "unknown",
}

language_name = st.selectbox(
    "🌐 Select input language",
    options=list(LANGUAGES.keys()),
)

language_code = LANGUAGES[language_name]

st.caption(
    f"Sarvam language code: `{language_code}`"
)


# =========================================================
# Speaker Selection
# =========================================================

SPEAKERS = [
    "ratan",
    "rohan",
    "ishita",
    "ritu",
]

speaker = st.selectbox(
    "🔊 Select AI voice",
    options=SPEAKERS,
    index=0,
)


# =========================================================
# Voice Input
# =========================================================

st.subheader("🎤 Step 1 — Ask your question")

audio_file = st.audio_input(
    "Click here and record your question"
)


# =========================================================
# Speech → Text
# =========================================================

def speech_to_text(audio_bytes, language_code):

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

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# =========================================================
# LLM Response
# =========================================================

def generate_answer(question):

    system_prompt = """
You are a helpful, accurate, and friendly general-purpose AI assistant.

The user can ask questions about any topic, including technology,
programming, science, mathematics, education, business, finance,
travel, daily life, writing, communication, current affairs,
or any other general topic.

Guidelines:

1. Answer the user's question directly and clearly.
2. Keep answers concise but provide enough detail to be useful.
3. Explain difficult concepts in simple language.
4. Use examples when they help understanding.
5. Do not invent or fabricate facts.
6. If you are uncertain, clearly say so.
7. For mathematical or technical questions, show the important steps.
8. If the question contains a formula, explain the formula clearly.
9. Respond in the same language as the user whenever possible.
10. For multilingual or code-mixed questions, understand the intent
    and respond naturally.
11. Maintain a friendly and professional tone.
12. Write responses that sound natural when spoken aloud.
13. Avoid unnecessary tables, complex formatting, or very long lists
    unless the user asks for them.
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


# =========================================================
# Text → Speech
# =========================================================

def text_to_speech(
    text,
    language_code,
    speaker
):

    response = client.text_to_speech.convert(

        text=text,

        model="bulbul:v3",

        language_code=language_code,

        speaker=speaker,

        pace=1.0,

        speech_sample_rate=24000,
    )

    return response


# =========================================================
# Process Voice
# =========================================================

if audio_file:

    st.audio(
        audio_file,
        format="audio/wav"
    )

    st.divider()

    if st.button(
        "🚀 Process Voice",
        type="primary",
        use_container_width=True,
    ):

        # =================================================
        # STEP 1 — Speech to Text
        # =================================================

        st.subheader(
            "🎤 Step 1 — Speech to Text"
        )

        with st.spinner(
            "Converting your voice to text..."
        ):

            try:

                stt_response = speech_to_text(
                    audio_file.getvalue(),
                    language_code,
                )

                transcript = (
                    stt_response.transcript
                )

            except Exception as e:

                st.error(
                    f"Speech-to-text failed:\n\n{e}"
                )

                st.stop()


        st.success(
            "Speech converted successfully."
        )

        st.markdown("### 📝 Your Question")

        st.info(transcript)


        # =================================================
        # STEP 2 — LLM
        # =================================================

        st.subheader(
            "🤖 Step 2 — AI Response"
        )

        with st.spinner(
            "Generating AI response..."
        ):

            try:

                answer = generate_answer(
                    transcript
                )

            except Exception as e:

                st.error(
                    f"AI response failed:\n\n{e}"
                )

                st.stop()


        st.success(
            "AI response generated."
        )

        st.markdown("### 💡 AI Answer")

        st.write(answer)


        # =================================================
        # STEP 3 — Text to Speech
        # =================================================

        st.subheader(
            "🔊 Step 3 — AI Voice Response"
        )


        # -------------------------------------------------
        # Determine TTS language
        # -------------------------------------------------

        tts_language_code = language_code

        if language_code == "unknown":

            detected_language = getattr(
                stt_response,
                "language_code",
                None,
            )

            if detected_language:

                tts_language_code = (
                    detected_language
                )

            else:

                tts_language_code = "en-IN"


        with st.spinner(
            "Generating AI voice..."
        ):

            try:

                tts_response = text_to_speech(
                    answer,
                    tts_language_code,
                    speaker,
                )

            except Exception as e:

                st.error(
                    f"Text-to-speech failed:\n\n{e}"
                )

                st.stop()


        # =================================================
        # Decode Audio
        # =================================================

        try:

            audio_base64 = (
                tts_response.audios[0]
            )

            audio_bytes = base64.b64decode(
                audio_base64
            )

        except Exception as e:

            st.error(
                f"Unable to decode audio:\n\n{e}"
            )

            st.stop()


        # =================================================
        # Play Audio
        # =================================================

        st.success(
            "AI voice generated successfully."
        )

        st.audio(
            audio_bytes,
            format="audio/wav",
        )


        # =================================================
        # Summary
        # =================================================

        st.divider()

        st.subheader(
            "✅ Voice Pipeline Completed"
        )

        st.write(
            "🎤 Speech"
            " → "
            "📝 Saaras STT"
            " → "
            "🤖 Sarvam LLM"
            " → "
            "🔊 Bulbul TTS"
        )