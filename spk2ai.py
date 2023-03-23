import os
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

chat_history = []

#

def ask_ai(input_text, temperature=0.3, add_to_history=True):
    """Ask AI a question and get the response with text.

    Args:
        input_text (str): Text to be sent to AI.
        temperature (float, optional): Temperature of the model. Value between 0 and 1. Defaults to 0.3.
        add_to_history (bool, optional): Whether the input/response pair should be put into the chat history. Defaults to True.

    Returns:
        str: Response text from AI.
    """
    global chat_history

    messages = []
    for x, y in chat_history:
        messages.append({"role": "user", "content": x})
        messages.append({"role": "assistant", "content": y})
    messages.append({"role": "user", "content": input_text})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    response_text = response.choices[0].message.content
    if add_to_history:
        chat_history.append((input_text, response_text))
    
    return response_text

#

#
# For debugging.
c = 0
#
while True:
    is_interrupting = False
    is_exiting = False
    print(f"[{len(chat_history)}] Me: ", end="", flush=True)
    #
    # For debugging.
    c += 1
    if c == 1:
        input_text = "请念李白的静夜思"
        continue
    elif c >= 2 and c <= 3:
        time.sleep(2)
        input_text = "李白是谁"
    elif c >= 4 and c <= 5:
        time.sleep(2)
        input_text = "等一等, 不要说了"
    elif c >= 6 and c < 7:
        time.sleep(2)
        input_text = "退出"
    elif c >= 7:
        break
    else:
    #
        input_text = speech_recognizer.recognize_once_async().get().text
    print(input_text + "\n")

    #
    # For debugging.
    print(f"(DEBUG) is_speaking: {is_speaking}")
    #
    if is_speaking:
        temp_response_text = ask_ai(
            f"假设当你正在说你刚才那句话时候我说: '{input_text}'. 你觉得我是否是想打断你说话？如果是请回答 'Y'，如果否或不确定请回答 'N'. 回答不要包含标点符号.",
            temperature=0.0,
            add_to_history=False)
        #
        # For debugging.
        print(f"(DEBUG) is_interrupting: {temp_response_text}")
        #
        if temp_response_text == "Y":
            speech_synthesizer.stop_speaking()
            is_interrupting = True
        continue

    temp_response_text = ask_ai(
        f"如果我接下来说: '{input_text}'. 你觉得我是否是想离开？如果是请回答 'Y'，如果否或不确定请回答 'N'. 回答不要包含标点符号.",
        temperature=0.0,
        add_to_history=False)
    #
    # For debugging.
    print(f"(DEBUG) is_exiting: {temp_response_text}")
    #
    if temp_response_text == "Y":
        is_exiting = True

    response_text = ask_ai(input_text)

    print(f"[{len(chat_history) - 1}] AI: " + response_text.strip() + "\n")
    ssrf = speech_synthesizer.speak_text_async(response_text)

    if is_exiting:
        ssrf.get()
        break

#
# (END)
