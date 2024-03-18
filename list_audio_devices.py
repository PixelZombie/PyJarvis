import pyaudio

def list_audio_devices():
    pa = pyaudio.PyAudio()
    info = pa.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    #for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
    for i in range(0, numdevices):
        if (pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", pa.get_device_info_by_host_api_device_index(0, i).get('name'))

    pa.terminate()

if __name__ == '__main__':
    list_audio_devices()