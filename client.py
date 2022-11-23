import socket
import threading
import pyaudio
import json
import numpy
import time



class VoiceClient:
    def __init__(self, ip=None, port=None, audio_format=pyaudio.paInt16, channels=1, rate=44100, frame_chunk=4096, audioIn=pyaudio.PyAudio(), audioOut=pyaudio.PyAudio(), input_device_id = None, output_device_id = None):
        self.running = False
        self.connected = False

        self.server_ip = socket.gethostbyname(ip)
        self.port = port

        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frame_chunk = frame_chunk
        self.__input_device = input_device_id
        self.__output_device = output_device_id
        self.__audioIn = audioIn
        self.__streamIn = None
        self.__audioOut = audioOut
        self.__streamOut= None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_wait_time = 5

    def start_stream(self):
        if self.running:
            print('Client already running!')
        else:
            self.running = True
            thread = threading.Thread(target=self.streaming)
            thread.start()
            print('Client streaming!')

    def streaming(self):
        counter = 0
        while counter < 60*self.connection_wait_time:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_ip, self.port))
                break
            except socket.error as error:
                print("Connection Failed **BECAUSE:** "+str(error))
                print("Attempt "+str(counter)+" of "+str(60*self.connection_wait_time))
                self.connected = False
                counter += 1
                time.sleep(1)        
        print('Connected to: '+str(self.server_ip)+':'+str(self.port))
        self.connected = True
        self.__streamIn = self.__audioIn.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frame_chunk,input_device_index=self.__input_device)
        
        while self.running:
            data = self.__streamIn.read(self.__frame_chunk)
            # decoded = numpy.frombuffer(data, dtype=numpy.uint16)
            self.socket.send(data)

    def start_receive(self):
        thread = threading.Thread(target=self.receive)
        thread.start()

    def receive(self):
        self.__streamOut = self.__audioOut.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, output=True, frames_per_buffer=self.__frame_chunk,output_device_index=self.__output_device)
        while self.connected:
            data = self.socket.recv(self.__frame_chunk)
            # print(data)
            # encoded = numpy.ndarray.tobytes(data)
            self.__streamOut.write(data)


def get_io():
    pya = pyaudio.PyAudio()
    info = pya.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    input_devices = {}
    output_devices = {}
    for i in range(0, numdevices):
        if pya.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
            input_devices[i] = pya.get_device_info_by_host_api_device_index(0, i)
        if pya.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
            output_devices[i] = pya.get_device_info_by_host_api_device_index(0, i)    
    return {'Input':input_devices,'Output':output_devices}

def filter_io(io, properties = ['index','name']):
    inputs = io['Input']
    outputs = io['Output']
    realized_in = {}
    realized_out = {}
    for i in inputs:
        realized_in[i] = {}
        for idx in properties:
            realized_in[i][idx] = inputs[i].get(idx)
    for i in outputs:
        realized_out[i] = {}
        for idx in properties:
            realized_out[i][idx] = outputs[i].get(idx)
    return {'Input':realized_in,'Output':realized_out}


if __name__=='__main__':

    ip = '192.168.56.1'
    port = 8080

    print('Starting client')

    filtered_io = filter_io(get_io(), ['index','name'])
    # print(json.dumps(filtered_io, indent=4))
    for i in filtered_io['Input']:
        print(filtered_io['Input'][i]['index'],filtered_io['Input'][i]['name'])
    input_id = int(input('Select Input Device ID: '))
    
    for i in filtered_io['Output']:
        print(filtered_io['Output'][i]['index'],filtered_io['Output'][i]['name'])
    output_id = int(input('Select Output Device ID: '))

    client = VoiceClient(ip = ip, port=port, input_device_id=input_id, output_device_id=output_id)
    client.start_stream()
    client.start_receive()