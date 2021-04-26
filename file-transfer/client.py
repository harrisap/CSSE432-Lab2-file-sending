import socket
import sys
import os
import tqdm

def client_program():
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server_(IP)_address> <server_port_number>")
        sys.exit()


    port = int(sys.argv[2])
    server_addr = (sys.argv[1], port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(server_addr)

    message = input(" -> ")

    while message.lower().strip() != ';;;':
        client_socket.send(message.encode())

        data = client_socket.recv(1024).decode()

        print("Received from server: " + str(data))

        message = input(" -> ")

    client_socket.close()


if __name__ == '__main__':
    client_program()
