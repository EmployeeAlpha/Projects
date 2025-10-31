import os
import json
from google.cloud import texttospeech

# Paths
KEY_PATH = "demellostips-key.json"
QUOTES_FILE = "Lex's Tips With Commas.txt"
OUTPUT_DIR = "audio_output"

# Set environment variable for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# Load quotes
with open(QUOTES_FILE, "r", encoding="utf-8") as f:
    quotes = eval("[" + f.read().strip().rstrip(',') + "]")  # Rebuilds the list safely

# Create output folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Google TTS client
client = texttospeech.TextToSpeechClient()

# Voice settings
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-D"
)

audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

# Generate audio
for i, quote in enumerate(quotes, 1):
    synthesis_input = texttospeech.SynthesisInput(text=quote)
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    filename = os.path.join(OUTPUT_DIR, f"quote_{i:03}.mp3")
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    print(f"Saved: {filename}")

print("✅ All quotes converted to MP3.")
