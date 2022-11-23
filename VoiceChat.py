import pyaudio
import socket
import threading
import time
import json
import socket
import threading
import pyaudio
import json
import numpy
import time

class VoiceServer:

  def __init__(self,host=None, port=None, frame_chunk=4096):
    self.running = False

    self.host = host
    self.port = port
    
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((self.host, self.port))

    self.frame_chunk = frame_chunk

    self.audio_data = []

    self.connections = {}

  def start_server(self):
    if self.running:
      print('Server already running!')
    else:
      self.running = True
      thread = threading.Thread(target=self.listening)
      thread.start()
      print('Server listening!')

  def server_info(self):
    starttime = time.time()
    while self.running:
      print(json.dumps({
        "Running":self.running,
        "Server IP":self.host,
        "Server Port":self.port,
        "Connections":self.connections
      }, indent=4)
      )
      time.sleep(60.0 - ((time.time() - starttime) % 60.0))
      

  def listening(self):
    self.socket.listen(50)
    server_info_thread = threading.Thread(target=self.server_info)
    server_info_thread.start()
    while self.running:
      connection, address = self.socket.accept()
      thread = threading.Thread(target=self.connection,
                                args=(
                                  connection,
                                  address,
                                ))
      thread.start()
      
      

  def connection(self, connection, address):
    print('Client connected!')
    print(connection, address)
    self.connections[address[0]] = {'Connection':str(connection),'Address':str(address)}
    while self.running:
        try:
          data = connection.recv(self.frame_chunk)
          connection.send(data)
        except ConnectionResetError:
          print('Connection was reset')
        except ConnectionError:
          print('Error with connection')

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

