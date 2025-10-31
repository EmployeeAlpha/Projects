import os
import re
import time
from google.cloud import texttospeech_v1beta1 as texttospeech

# Set up Google Cloud client
client = texttospeech.TextToSpeechClient()

# File paths
input_file = "Lex's Tips With Commas.txt"
output_folder = "audio_output"
os.makedirs(output_folder, exist_ok=True)

# Read and parse quotes
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()
    content = re.sub(r"[“”]", '"', content)  # Normalize curly quotes
    quotes = eval("[" + content.strip().rstrip(',') + "]")

# Google Cloud voice configuration (Studio-quality Male voice)
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-M",
)

audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

# Generate speech files
for idx, quote in enumerate(quotes, 1):
    file_path = os.path.join(output_folder, f"quote_{idx:03}.mp3")
    if os.path.exists(file_path):
        continue  # Skip already processed files

    synthesis_input = texttospeech.SynthesisInput(text=quote)

    try:
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        with open(file_path, "wb") as out:
            out.write(response.audio_content)
        print(f"✅ Saved: {file_path}")
        time.sleep(0.1)  # Mild rate limit to be gentle
    except Exception as e:
        print(f"❌ Failed to synthesize quote {idx}: {e}")
