import os
import pyaudio
import socket
import threading
import time
from pyngrok import conf, ngrok

host = socket.gethostbyname(socket.gethostname())
port = 8080

NGROK_TOKEN = os.environ['NGROK_TOKEN']

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
      print({
        "Running":self.running,
        "Server IP":self.host,
        "Server Port":self.port,
        "Connections":self.connections
      })
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
    self.connections[address] = {'Connection':connection,'Address':address}
    while self.running:
        data = connection.recv(self.frame_chunk)
        connection.send(data)


if __name__=='__main__':
  print('Starting Server...')

  ngrok.set_auth_token(NGROK_TOKEN)
  conf.get_default().region = "eu"
  ngrok_tunnel = ngrok.connect(port,'tcp')
  print(ngrok_tunnel)
  
  server = VoiceServer(host = host, port = port)
  server.start_server()
  