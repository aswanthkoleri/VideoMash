import speech_recognition as sr

r=sr.Recognizer()

audioFile = sr.AudioFile('harvard.wav')
with audioFile as source:
    audio = r.record(source)
WIT_API_KEY="BAVSMY4FFLS6JWCUTML7JYGVOZWA5Q4E"
result=r.recognize_wit(audio,WIT_API_KEY)

print(result)