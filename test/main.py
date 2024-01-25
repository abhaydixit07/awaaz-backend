from openai import OpenAI
client = OpenAI(api_key="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")

audio_file= open("output.wav", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file,
  response_format="text"
)
print(transcript)