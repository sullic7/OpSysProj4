import socket
import thread

BUFFER_SIZE = 1024
LISTENER_PORT = 8764


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5) # this is the number of possible queued connections
    while 1:
        print("Waiting for a new connection.")
        client_socket, client_address = server_socket.accept()
        print("Received a new connection from %s:%s" % client_address)
        thread.start_new_thread(handel_new_conection, (client_socket, client_address))

def handel_new_conection(client_socket, client_address):
    print("Time to handle the client at %s:%s!" % client_address)
    # first we have to get the command from the client
    while 1:
        data = client_socket.recv(BUFFER_SIZE)

        if not data:
            print("Didn't get any data from the client, abandoning.")
            break;
        print("data: "+ repr(data))

        # DO SOMETHING HERE TO GET CLIENT RESPONSE
        # until then the server just flirts with the client
        response = "Hey baby, come here often? I'll be your server today."
        
        print("response: "+ repr(response))
        client_socket.send(response)

    print("client closed connection :'-(. I guess no one wants to talk to me.")


if __name__ == '__main__':
    start_server('', LISTENER_PORT)