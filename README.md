# Sarvam AI Voice Assistant

A general-purpose multilingual voice assistant built using **Sarvam AI** and **Streamlit**.

The application provides an end-to-end voice interaction pipeline:

**Speech → Speech-to-Text → LLM → Text-to-Speech → Voice Response**

The solution uses Sarvam's speech and language models to provide a natural conversational experience, with a focus on Indian languages and accents.

---

## Architecture

```text
                         USER
                           │
                           │
                    🎤 Voice Input
                           │
                           ▼
              ┌────────────────────────┐
              │       STREAMLIT         │
              │      Web Interface     │
              └────────────┬───────────┘
                           │
                           │ Audio
                           ▼
              ┌────────────────────────┐
              │       STT              │
              │    Saaras v3           │
              │                        │
              │ Speech → Text           │
              └────────────┬───────────┘
                           │
                           │ Transcribed Text
                           ▼
              ┌────────────────────────┐
              │        LLM             │
              │     Sarvam-105B        │
              │                        │
              │ Understanding          │
              │ Reasoning              │
              │ Response Generation   │
              └────────────┬───────────┘
                           │
                           │ Generated Text
                           ▼
              ┌────────────────────────┐
              │        TTS             │
              │      Bulbul v3         │
              │                        │
              │ Text → Speech           │
              └────────────┬───────────┘
                           │
                           │ Audio
                           ▼
              ┌────────────────────────┐
              │       STREAMLIT        │
              │    Audio Playback      │
              └────────────┬───────────┘
                           │
                           ▼
                         USER
```
## Architecture

The application follows this architecture:

```text
User
  ↓
Streamlit
  ↓
Saaras v3 - STT
  ↓
Sarvam-105B - LLM
  ↓
Bulbul v3 - TTS
  ↓
User
```

## 1. Saaras v3 - Speech-to-Text

**Model ID:** `saaras:v3`

Saaras v3 converts the user's speech into text.

### Example

```text
User speaks:
"What is artificial intelligence?"

Saaras v3 produces:
"What is artificial intelligence?"
```

## 2. Sarvam-105B - Large Language Model

**Model ID:** `sarvam-105b`

Sarvam-105B receives the text from STT and generates the AI response.

### Example

```text
Input:
What is artificial intelligence?

Output:
Artificial intelligence is a field of computer science...
```

## 3. Bulbul v3 - Text-to-Speech

**Model ID:** `bulbul:v3`

Bulbul v3 converts the LLM response into natural speech.

### Example

```text
LLM Response:
"Artificial intelligence is a field of computer science..."

Bulbul v3:
🔊 Audio response
```
