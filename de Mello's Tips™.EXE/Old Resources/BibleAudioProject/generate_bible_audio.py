import os
import pandas as pd
from google.cloud import texttospeech

# STEP 1: Set your service account key file here
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bibleverseaudioproject-60fe34218b00.json"  # <- CHANGE THIS

# STEP 2: Load the matched CSV file
df = pd.read_csv("Final_Tips_With_KJV_Matches.csv")

# STEP 3: Configure Google TTS client
client = texttospeech.TextToSpeechClient()

voice = texttospeech.VoiceSelectionParams(
    language_code="en-GB",  # British English
    name="en-GB-Neural2-C",  # Distinct from your male voice
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.98,  # Calm and readable
    pitch=0.0
)

# STEP 4: Loop through all 551 rows and generate MP3s
for idx, row in df.iterrows():
    quote_num = idx + 1
    verse = str(row["Related Bible Passage (KJV)"])
    reference = str(row["KJV Reference"])

    # Customize spoken format
    text = f"{verse} — {reference}."

    synthesis_input = texttospeech.SynthesisInput(text=text)

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    filename = f"bible_{quote_num:03}.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f"✅ Saved: {filename}")

print("🎉 All 551 Bible MP3s generated successfully!")
