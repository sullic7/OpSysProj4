import socket
import thread
import threading
import string
from SimulatedDisk import SimulatedDisk, SimulatedDiskError
import signal
import sys

BUFFER_SIZE = 1024
LISTENER_PORT = 8765


def start_server(host, port, disk):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5) # this is the number of possible queued connections
        print("Listening on port %d" % port)
        while 1:
            client_socket, client_address = server_socket.accept()
            print("Received incoming connection from %s:%s" % client_address)
            thread.start_new_thread(handle_new_conection, (client_socket, client_address, disk))
    except KeyboardInterrupt:
        pass
    finally:
        # close the port and exit gracefully
        print("Closing server socket")
        server_socket.close()

def handle_new_conection(client_socket, client_address, disk):
    # first we have to get the command from the client
    threadID = threading.currentThread().ident
    try:
        while 1:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                client_socket.send("ERROR: NO DATA ENTERED FROM CLIENT\n")
                break;

            # DO SOMETHING HERE TO GET CLIENT RESPONSE
            # first strip the string of the random "\r" I see from telnet
            data = string.replace(data, "\r", "")

            try:
                response = parse_request_and_formulate_response(data, disk)
            except Exception as e:
                # this is a catch all response
                response = "ERROR: %s" % (threadID, str(e))
            
            client_socket.send(response)
    finally:
        print("[thread %d] Client closed its socket....terminating" % threadID)
        client_socket.close()

def parse_request_and_formulate_response(request, disk):
    # replace \n with spaces because that's only reasonable
    # then remove the trailing space
    request = request.replace("\n", " ")
    request = request.strip()
    current_thread = threading.currentThread().ident

    print("[thread %d] Rcvd:" % current_thread),
    print request

    # split the request and pass it to the proper function
    split_request = request.split()
    split_request.append(current_thread)

    # I use a few extra cycles here to use some sexy syntax below
    command = split_request.pop(0)

    if command == 'STORE':
        split_request[1] = int(split_request[1])
        return disk.store(*split_request)

    if command == 'READ':
        split_request[1] = int(split_request[1])
        split_request[2] = int(split_request[2])
        return disk.read(*split_request)

    if command == 'DELETE':
        return disk.delete(*split_request)

    if command == 'DIR':
        return disk.dir(current_thread)
    # if we haven't returned by now there's an error
    # print("[thread %d] ERROR: Invalid command" % current_thread)
    return "ERROR: INVALID COMMAND\n"


if __name__ == '__main__':
    disk = SimulatedDisk(256)
    start_server('', LISTENER_PORT, disk)