# PyJarvis

A Jarvis-like assistant integrating Jan.AI, Whisper, TTS and picovoice porcupine in Python
Goal is to have a simple and easy to use assistant that can be used without an internet connection besides installing stuff 

## Prerequisites

- Python 3.11
- picovoice porcupine access key for the wakeword detection (free account available at https://picovoice.ai/console/)
- Jan.AI installed and webserver running

## ToDo's
- winsound is in use at the moment since it is developed on Windows, should be replaced with something else for other OS
- wakeword detection via picovoice porcupine should be replaced with and offline solution
