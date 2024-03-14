# Start by making sure the `assemblyai` package is installed.
# If not, you can install it by running the following command:
# pip install -U assemblyai
#
# Note: Some macOS users may need to use `pip3` instead of `pip`.

import assemblyai as aai
aai.settings.api_key = "e00b9b4c3d6840b3b27b68aac187c325"
audio_url = "a.mp3"
transcriber = aai.Transcriber()
transcript = transcriber.transcribe(audio_url)

if transcript.status == aai.TranscriptStatus.error:
    print(transcript.error)
else:
    print(transcript.text)



config = aai.TranscriptionConfig(sentiment_analysis=True,  speaker_labels=True, entity_detection=True, summarization=True,
  summary_model=aai.SummarizationModel.informative,
  summary_type=aai.SummarizationType.bullets)
transcript = aai.Transcriber().transcribe(audio_url, config)

print("\n")
print(" Speaker Types \n")
for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")

print(" sentiment results \n ")
for sentiment_result in transcript.sentiment_analysis:
    print("\n", sentiment_result.text)
    print("sentiment - ",sentiment_result.sentiment, "confidence - ", sentiment_result.confidence)

print(" entities \n ")
for entity in transcript.entities:
    print("text- ", entity.text, "  type- ", entity.entity_type)

print("summary       \n ", transcript.summary,"\n")

