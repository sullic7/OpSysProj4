import socket
import thread
import threading
import string
import signal
import sys

BUFFER_SIZE = 4096
LISTENER_PORT = 8765

def start_client(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect((host, port))

        test_server(client_socket)
    except KeyboardInterrupt:
        pass
    finally:
        # close the port and exit gracefully
        print("Closing client socket")
        client_socket.close()

def test_server(client_socket):
    command_list = ["STORE xyz.txt 11\nHelloWorld\n",
                    "DIR\n",
                    "STORE abc.txt 20\nHereIsTwentyCharacs\n",
                    "READ abc.txt 6 6\n",
                    "DIR\n",
                    "DELETE xyz.txt\n",
                    "READ xyz.txt 5 3\n",
                    "DIR\n"]
    for command in command_list:
        try:
            print("Sending command: %s" % command)
            response = send_command(client_socket, command)
            print("Got Response:\n%s\n" % response)
        except Exception as e:
            print("Caught error '%s' in sending command." % str(e))
            response = "Error sending command\n"

def send_command(client_socket, command):
    client_socket.send(command)
    comm = command.split(" ")[0]
    return client_socket.recv(BUFFER_SIZE)

if __name__ == '__main__':
    start_client('localhost', LISTENER_PORT)