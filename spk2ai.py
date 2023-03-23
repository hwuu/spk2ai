import json
import time
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

is_speaking = False
speech_synthesizer.synthesis_started.connect(lambda _: globals().update(is_speaking=True))
speech_synthesizer.synthesis_completed.connect(lambda _: globals().update(is_speaking=False))
speech_synthesizer.synthesis_canceled.connect(lambda _: globals().update(is_speaking=False))

#

history = []
#
# For debugging.
#c = 0
#
while True:
    is_exiting = False
    print(f"[{len(history)}] Me: ", end="", flush=True)
    #
    # For debugging.
    #c += 1
    #if c == 1:
    #    input_text = "请念李白的静夜思"
    #elif c >= 2:
    #    time.sleep(2)
    #    input_text = "李白是谁"
    #elif c == 3:
    #    break
    #else:
    #
    result = speech_recognizer.recognize_once_async().get()
    input_text = result.text
    print(input_text + "\n")

    #
    # For debugging.
    #print(f"(DEBUG) is_speaking: {is_speaking}")
    #
    if is_speaking:
        temp_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"我在和某人对话, 正当我说到一半的时候他说: '{input_text}'. 请问他是否是想打断我说话？如果是请回答 'Y'，如果否或不确定请回答 'N'. 回答不要包含标点符号.",
            }],
            temperature=0.0,
        )
        temp_response_text = temp_response.choices[0].message.content.strip()
        #
        # For debugging.
        #print(f"(DEBUG) is_to_interrupt: {temp_response_text}")
        #
        if temp_response_text == "Y":
            speech_synthesizer.stop_speaking()
        time.sleep(2)
        continue

    temp_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"我在和某人对话，他说: '{input_text}'. 请问他是否是想离开？如果是请回答 'Y'，如果否或不确定请回答 'N'. 回答不要包含标点符号.",
        }],
        temperature=0.0,
    )
    temp_response_text = temp_response.choices[0].message.content.strip()
    if temp_response_text == "Y":
        is_exiting = True

    messages = []
    for x, y in history:
        messages.append({"role": "user", "content": x})
        messages.append({"role": "assistant", "content": y})
    messages.append({"role": "user", "content": input_text})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    response_text = response.choices[0].message.content
    history.append((input_text, response_text))

    print(f"[{len(history) - 1}] AI: " + response_text.strip() + "\n")
    ssrf = speech_synthesizer.speak_text_async(response_text)

    if is_exiting:
        ssrf.get()
        break

#
# (END)
