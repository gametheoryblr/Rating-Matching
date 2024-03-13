import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key   = os.getenv('ASSEMBLYAI_API_KEY')
transcriber = aai.Transcriber()

#for all mp3 files in the current directory
for file in os.listdir('./data'):
    if file.endswith('.mp3'):
        audio = "./data/"+file
        config = aai.TranscriptionConfig(speaker_labels=True)

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(
        audio,
        config=config
        )
        string = ""
        for utterance in transcript.utterances:
            string= string + utterance.speaker + " " + utterance.text + "\n"

        with open(f"{audio}_transcript.txt", 'a') as f:
            f.write(string)
            f.close()

        print(f"Transcription of {audio} complete")
    





