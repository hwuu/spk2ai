import os
import json
import requests

import openai
import azure.cognitiveservices.speech as speechsdk


with open("config.json", "r") as f:
    config = json.load(f)

speech_region = config["speech_region"]
speech_key = config["speech_key"]
openai.api_key = config["openai_api_key"]


def speech_recognize_from_microphone():
    """使用麦克风进行语音识别"""
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    print("开始说话...")
    result = speech_recognizer.recognize_once_async().get()
    return result.text


def text_to_speech(text):
    """将文本转换成语音输出"""
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_text_async(text).get()


def send_message_to_chat_api(message):
    """将对话内容发送到后台文本聊天API"""
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=message,
        temperature=0.3,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["."])
    return response.choices[0].text


def run_dialog():
    """运行语音对话程序"""
    exit = False
    while True:
        # 语音输入
        user_input = speech_recognize_from_microphone()
        print("你说: " + user_input)

        if user_input.lower() == "exit.":
            user_input = "That's all for today. Bye."
            exit = True

        # 将语音输入发送到后台文本聊天API进行处理
        bot_response = send_message_to_chat_api(user_input)
        print("机器人说: " + bot_response.strip() + "\n\n")

        # 将机器人的文本回复转换成语音输出
        text_to_speech(bot_response)

        if exit:
            break


if __name__ == '__main__':
    run_dialog()
