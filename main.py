import os
import pyaudio
import wave
import pvporcupine
import struct
import numpy as np
import requests
import whisper
from TTS.api import TTS
import winsound

config = {
    "language": "de",
    "input_device_index": 1, # get it from list_audio_devices.py
    "whisperModel": "medium",
    "janAPI": "http://localhost:1337/v1/chat/completions",
    "janModel": "mixtral-8x7b-instruct",
    "janModelInstructions": "Du bist Jarvis. Du antwortest auf meine Fragen in informalem deutsch und führst Befehle aus. Du bist nüchtern und antwortest in so wenig Sätzen wie möglich. Du dutzt mich wenn du mich ansprichst.",
    "ttsModelName": "tts_models/de/thorsten/tacotron2-DDC",
    "porcupineAccessKey": os.environ["PORCUPINE_ACCESS_KEY"] + "=="
}

whisperModel = whisper.load_model(config["whisperModel"])

url = "http://localhost:1337/v1/chat/completions"

# add == to the end of the key since vscode doesn't allow to set environment variables with == at the end
pvporcupine_access_key = config["porcupineAccessKey"]
tts = TTS(model_name=config["ttsModelName"]) # replace with multi lingual model



def speech_to_text(filename):
    result = whisperModel.transcribe(filename, language=config["language"])
    print("speech to text: ", result["text"])
    process_command(result["text"])

def text_to_speech(text):
    print("text to speech: ", text)
    output_file = "output.wav"
    tts.tts_to_file(text, file_path=output_file)
    winsound.PlaySound(output_file, winsound.SND_FILENAME)
    

def process_command(command):
    url = config["janAPI"]
    payload = {
        "messages": [
            {
                "content": config["janModelInstructions"],
                "role": "system"
            },
            {
                "content": command,
                "role": "user"
            }
        ],
        "model": config["janModel"],
        "stream": False,
        "max_tokens": 2048,
        "stop": None,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "temperature": 0.7,
        "top_p": 0.95
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            # Assuming the first choice contains the relevant response
            first_choice = response_json['choices'][0]
            if 'message' in first_choice and 'content' in first_choice['message']:
                assistant_message = first_choice['message']['content']
                print("Assistant:", assistant_message)
                text_to_speech(assistant_message)
            else:
                print("Response parsing error: 'message' or 'content' not found")
        else:
            print("Response parsing error: 'choices' not found or empty")
    else:
        print("Failed to process command, status code:", response.status_code)
        print("Response:", response.text)
    

def main():
    porcupine = None
    pa = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(access_key=pvporcupine_access_key, keywords=["jarvis"])

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=config["input_device_index"],
        )

        print("Listening for wake word...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm_unpacked)

            if keyword_index >= 0:
                print("Wake word detected. Recording command...")
                frames = []
                for _ in range(0, int(porcupine.sample_rate / porcupine.frame_length * 3)):
                    data = audio_stream.read(porcupine.frame_length)
                    frames.append(data)
                wav_data = b''.join(frames)

                # Save the recorded command to a file (optional)
                filename = "command.wav"
                wf = wave.open(filename, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(porcupine.sample_rate)
                wf.writeframes(wav_data)
                wf.close()

                # Convert byte data to NumPy array to make it compatible with most audio processing libraries
                np_audio_data = np.frombuffer(wav_data, dtype=np.int16)
                # transcribe with whisper
                speech_to_text(filename)

    except KeyboardInterrupt:
        print('Stopping...')
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()


if __name__ == '__main__':
    #list_audio_devices()
    main()
