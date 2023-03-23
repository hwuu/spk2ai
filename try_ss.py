import os
import json
import time
import argparse

import azure.cognitiveservices.speech as speechsdk

#

parser = argparse.ArgumentParser()
parser.add_argument('--config', help='config file in JSON format')
args = parser.parse_args()

config_file_path = "config.json" if args.config is None else args.config
with open(config_file_path, "r") as f:
    config = json.load(f)

speech_config = speechsdk.SpeechConfig(subscription=config["speech_key"], region=config["speech_region"])
speech_config.speech_synthesis_language = config["language"]
speech_config.speech_synthesis_voice_name = "%s-%sNeural" % (config["language"], config["voice"])

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

is_speaking = False
speech_synthesizer.synthesis_started.connect(lambda _: globals().update(is_speaking=True))
speech_synthesizer.synthesis_completed.connect(lambda _: globals().update(is_speaking=False))
speech_synthesizer.synthesis_canceled.connect(lambda _: globals().update(is_speaking=False))

#

ssrf = speech_synthesizer.speak_text_async("静夜思：床前明月光，疑是地上霜。")

for i in range(0, 10):
    if i == 4:
        speech_synthesizer.stop_speaking()
    print(i, is_speaking)
    time.sleep(1)

#
# (END)
