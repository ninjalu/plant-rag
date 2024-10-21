import whisper
import os

model = whisper.load_model("base")

folder = "audio"
for filename in os.listdir(folder):
    if filename.endswith(".mp3"):
        audio_path = os.path.join(folder, filename)

        # Transcribe the audio
        print(f"Transcribing {filename}...")
        result = model.transcribe(audio_path)

        # Save the transcription to a text file
        transcription_filename = f"{os.path.splitext(filename)[0]}_transcription.txt"
        with open(os.path.join(folder, transcription_filename), "w") as f:
            f.write(result["text"])

        print(f"Transcription saved to {transcription_filename}.")
