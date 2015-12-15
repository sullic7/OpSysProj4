import socket
import thread
import threading
import string
from SimulatedDisk import SimulatedDisk
import signal
import sys
import os

BUFFER_SIZE = 4096
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

            try:
                response = parse_request_and_formulate_response(client_socket, data, disk)
            except Exception as e:
                # this is a catch all response
                print("[thread %d] caught error '%s' in handling a request." % (threadID, str(e)))
                response = \
"""There was a runtime error in the code handling the
request. Please check the server log for more information.\n"""
            client_socket.send(response)
    finally:
        print("[thread %d] Client closed its socket....terminating" % threadID)
        client_socket.close()

def parse_request_and_formulate_response(client_socket, request, disk):
    current_thread = threading.currentThread().ident
    print("[thread %d] Rcvd:" % current_thread),
    print request

    # split the parse_request and pass it to the proper function
    split_request = request.split(" ")
    command = split_request[0]

    if command == 'STORE':
        filename = split_request[1]
        # split_request[2] is NUM_BYTES\nDATA
        split_again = split_request[2].split('\n', 1)
        # print("before split: %s" % split_request[2])
        # print("after split", split_again)
        num_bytes = int(split_again[0])
        file_contents = split_again[1]

        # so this is silly but if there are many newlines 
        # this will read in all the unread bytes

        if ".jpg" in filename:
            file_contents = file_contents.strip("\n")
            num_unread_bits = num_bytes*8 - len(file_contents)
            while num_unread_bits > 0:
                file_contents += client_socket.recv(BUFFER_SIZE).strip("\n")
                num_unread_bits = num_bytes*8 - len(file_contents)
        else:
            num_unread_bytes = num_bytes - len(file_contents)
            while num_unread_bytes > 0:
                file_contents += client_socket.recv(BUFFER_SIZE)
                num_unread_bytes = num_bytes - len(file_contents)

        return disk.store(filename, num_bytes, current_thread, file_contents)

    if command == 'READ':
        filename = split_request[1]
        byte_offset = int(split_request[2])
        length = int(split_request[3])
        return disk.read(filename, byte_offset, length, current_thread)

    if command == 'DELETE':
        # remove the trailing newline
        filename = split_request[1].strip()
        return disk.delete(filename, current_thread)

    if command == 'DIR\n':
        return disk.dir(current_thread)
    # if we haven't returned by now there's an error
    print("[thread %d] ERROR: Invalid command: %s" % (current_thread, command))
    return "ERROR: INVALID COMMAND\n"


if __name__ == '__main__':
    disk = SimulatedDisk(256)
    start_server('', LISTENER_PORT, disk)