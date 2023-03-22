# Speak to AI (now ChatGPT)

With this small program, you can speak to ChatGPT and get answers with a synthetic voice, like talking to a real person. Most of the code lines were generated by ChatGPT; I just did a little refinement.

Usage:

```
spk2ai.py [-h] [--config CONFIG]
```

Optional arguments:

  * `-h, --help`: Show help message and exit
  * `--config CONFIG`: Specify the path of the config file

Config file template:

```json
{
  "speech_region": "<region>",
  "speech_key": "<api key of Speech Service>",
  "openai_api_key": "<api key of ChatGPT>",
  "language": "zh-CN",
  "voice": "Xiaoxiao"
}
```

In the config file you can specify a language and a voice of the speech synthesizer, see details in:

* [Speech-to-text: Change the source language
](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-speech-synthesis?tabs=browserjs%2Cterminal&pivots=programming-language-python#select-synthesis-language-and-voice)
* [Text-to-speech: Select synthesis language and voice](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-speech-synthesis?tabs=browserjs%2Cterminal&pivots=programming-language-python#select-synthesis-language-and-voice)
