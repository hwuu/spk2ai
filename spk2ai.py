import os
import json
import requests

import openai
import azure.cognitiveservices.speech as speechsdk

#

with open("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config["openai_api_key"]

speech_config = speechsdk.SpeechConfig(subscription=config["speech_key"], region=config["speech_region"])
speech_config.speech_synthesis_language = "en-IN" # Default: "en-US"
speech_config.speech_synthesis_voice_name ="en-IN-PrabhatNeural" # Default: "en-US-JennyNeural"

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

history = []
to_exit = False

while True:
    print("Please start speaking...")
    result = speech_recognizer.recognize_once_async().get()
    input_text = result.text
    print("You said: " + input_text)

    if input_text.endswith("Exit."):
        input_text = "That's all for today. Bye."
        to_exit = True

    messages = []
    for x, y in history[-20:]:
        messages.append({"role": "user", "content": x})
        messages.append({"role": "assistant", "content": y})
    messages.append({"role": "user", "content": input_text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
        #max_tokens=4096,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    response_text = response.choices[0].message.content
    print("AI said: " + response_text.strip() + "\n")

    history.append((input_text, response_text))
    if len(history) > 100:
        history.pop(0)

    speech_synthesizer.speak_text_async(response_text).get()

    if to_exit:
        break

#
# (END)
