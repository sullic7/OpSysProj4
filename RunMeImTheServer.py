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
        print("closing server socket")
        server_socket.close()

def handle_new_conection(client_socket, client_address, disk):
    # first we have to get the command from the client
    try:
        while 1:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                print("Didn't get any data from the client, abandoning.")
                break;
            print("data: "+ repr(data))

            # DO SOMETHING HERE TO GET CLIENT RESPONSE
            # first strip the string of the random "\r" I see from telnet
            data = string.replace(data, "\r", "")

            try:
                # response = "Hey baby, come here often? I'll be your server today."
                response = parse_request_and_formulate_response(data, disk)
            except Exception as e:
                print("caught an exception")
                print(e)
                # this is a catch all response
                response = "ERROR: something bad happened. I'm sorry hon."
            
            #print("response: "+ repr(response))
            client_socket.send(response)
    finally:
        print("finally closing client socket")
        client_socket.close()

    print("client closed connection :'-(. I guess no one wants to talk to me.")


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
    command = split_request.pop(0)
    # I use a few extra cycles here to use some sexy syntax
    try:
        if command == 'STORE':
            split_request[1] = int(split_request[1])
            return disk.store(*split_request)

        if command == 'READ':
            split_request[1] = int(split_request[1])
            split_request[2] = int(split_request[2])
            return disk.read(*split_request)

        if command == 'DELETE':
            print("Trying to delete a file %s." % split_request[0])
            return disk.delete(*split_request)

        if command == 'DIR':
            print("Listing the files in the system.")
            return disk.dir(current_thread)
        # if we haven't returned by now there's an error
        return "ERROR: Invalid command\n"

    except SimulatedDiskError as e:
        print("sending back a simulated disk error: %s" % e)
        return str(e)


if __name__ == '__main__':
    disk = SimulatedDisk(256)
    start_server('', LISTENER_PORT, disk)