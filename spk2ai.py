import os
import re
import json
import argparse

import openai
import azure.cognitiveservices.speech as speechsdk

#

parser = argparse.ArgumentParser()
parser.add_argument('--config', help='config file in JSON format')
args = parser.parse_args()

config_file_path = "config.json" if args.config is None else args.config
with open(config_file_path, "r") as f:
    config = json.load(f)

openai.api_key = config["openai_api_key"]
speech_config = speechsdk.SpeechConfig(subscription=config["speech_key"], region=config["speech_region"])
speech_config.speech_recognition_language=config["language"]
speech_config.speech_synthesis_language = config["language"]
speech_config.speech_synthesis_voice_name = "%s-%sNeural" % (config["language"], config["voice"])

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

#

print("Please start speaking. You can say 'stop' to intercept the AI and say 'exit' to return to your real, yet boring, world.\n")

history = []
while True:
    print(f"[{len(history)}] Me: ", end="", flush=True)
    result = speech_recognizer.recognize_once_async().get()
    input_text = result.text
    print(input_text + "\n")

    response_text = ""
    cmd = re.sub(r'[^a-zA-Z]', ' ', input_text).strip().lower()
    if cmd == "stop":
        speech_synthesizer.stop_speaking()
        if config["language"].split("-")[0] == "zh":
            response_text = "好的, 请你先说."
        elif config["language"].split("-")[0] == "en":
            response_text = "OK. I'm listening."
    elif cmd == "exit":
        if config["language"].split("-")[0] == "zh":
            response_text = "好的, 再见."
        elif config["language"].split("-")[0] == "en":
            response_text = "OK. See you next time."
    else:
        messages = []
        for x, y in history:
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
        history.append((input_text, response_text))

    print(f"[{len(history)}] AI: " + response_text.strip() + "\n")
    f = speech_synthesizer.speak_text_async(response_text)

    if cmd == "stop":
        f.get()
    elif cmd == "exit":
        f.get()
        break

#
# (END)
