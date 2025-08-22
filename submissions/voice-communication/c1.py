import socket
import threading
import pyaudio
import random
import sys 

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <server_ip>")
    sys.exit(1)

HOST = sys.argv[1]  # Get IP from command-line argument
PORT = 12345

def receive_audio():
    while True:
        try:
            data = client_socket.recv(CHUNK)
            if not data:
                print("Disconnected from server.")
                break
            stream.write(data)
        except Exception as e:
            print(f"Error receiving audio: {e}")
            break

def send_audio():
    print("Connected to server.")
    while True:
        try:
            data = stream.read(CHUNK)
            client_socket.sendall(data)
        except Exception as e:
            print(f"Error sending audio: {e}")
            break

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
except Exception as e:
    print(f"Error connecting to server: {e}")
    sys.exit(1)

client_id = str(random.randint(10000, 99999))
print("Connected to server. Your client ID is:", client_id)
client_name = input("Enter your name: ")
client_socket.send(client_name.encode())

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

receive_thread = threading.Thread(target=receive_audio, daemon=True)
receive_thread.start()

send_thread = threading.Thread(target=send_audio, daemon=True)
send_thread.start()

receive_thread.join()
send_thread.join()
