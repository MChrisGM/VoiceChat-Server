import os
import socket
from pyngrok import conf, ngrok
from dotenv import load_dotenv

from VoiceChat import VoiceServer

if __name__=='__main__':
  print('Starting Server...')

  load_dotenv()

  host = socket.gethostbyname(socket.gethostname())
  port = 8080

  NGROK_TOKEN = os.environ['NGROK_TOKEN']

  # ngrok.set_auth_token(NGROK_TOKEN)
  # conf.get_default().region = "eu"
  # ngrok_tunnel = ngrok.connect(port,'tcp')
  # print(ngrok_tunnel)
  
  server = VoiceServer(host = host, port = port)
  server.start_server()
  