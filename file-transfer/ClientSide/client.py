import socket
import sys
import os
import tqdm
import os.path
from os import path

help_msg = "Valid commands are: iWant, uTake, help\nType ';;;' to exit."

SEPARATOR = "<SEPARATOR>"

BUFFER_SIZE = 1024


def client_program():
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server_(IP)_address> <server_port_number>")
        sys.exit()

    port = int(sys.argv[2])
    server_addr = (sys.argv[1], port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(server_addr)

    print(help_msg)

    #TODO connectionreseterror

    while True:
        message = input("> ")
        message = message.strip()
        if message == ';;;':
            break
        elif message == 'help':
            print(help_msg)
        else:

            command = message[0:5]

            if(command == "uTake"):

                # uTake command

                handleUTake(message, client_socket)
                    # file to send does not exist

            elif (command == "iWant"):

                # iWant command

                handleIWant(client_socket, message)

            else:
                print("not a valid command")
                # not a valid command

    client_socket.close()

def handleUTake(message, client_socket):
    if(path.exists(message[6:])):

        # file exists, send message

        filename = message[6:]
        filesize = os.path.getsize(filename)

        client_socket.send(message.encode())

        response = client_socket.recv(1024).decode()

        if(str(response) == "DATAI"):

            # server is requesting data info

            print("Server waiting for file information...")

            client_socket.send(
                f"{filename}{SEPARATOR}{filesize}".encode())

            response = client_socket.recv(1024).decode()

            if(str(response) == "YRECV"):

                print("Server accepted transfer!")

                sendFile(filename, client_socket)

            else:
                print("server did not accept request 1")
                # server did not accept request

        else:
            print("server did not accept request 2")

    else:
        print("file to send does not exist. cwd is:")
        print(os.getcwd())
        # file to send does not exist

def handleIWant(client_socket, message):
    client_socket.send(message.encode())

    data = client_socket.recv(1024).decode()

    if(data == "FILEE"):
        client_socket.send("DATAI".encode())

        data = client_socket.recv(1024).decode()

        try:
            recvfilename, recvfilesize = data.split(SEPARATOR)

            nfilename = os.path.basename(recvfilename)

            nfilesize = int(recvfilesize)

            savelocation = input("Save to > ")
            savelocation = savelocation.strip()

            client_socket.send("YRECV".encode())

            receiveFile(savelocation + f"/{nfilename}", client_socket)

        except ValueError:
            print("⚠ Bad structure for response data")

    else:
        print("File does not exist in server...")
        print("Got back: ")
        print(data)

def sendFile(filename, client_socket):
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file

            bytes_read = f.read(BUFFER_SIZE)

            if not bytes_read:
                # file transmission is finished
                print("File sent!")
                break

            client_socket.sendall(bytes_read)

    print("Done sending file")

def receiveFile(savelocation, client_socket):
    from pathlib import Path
    Path("recv/").mkdir(parents=True, exist_ok=True)

    with open(savelocation, "wb") as f:
        while True:

            bytes_read = client_socket.recv(BUFFER_SIZE)

            if not bytes_read:
                # nothing received
                print("File transfer finished.")
                break

            f.write(bytes_read)

        print("Finished recv")

if __name__ == '__main__':
    client_program()
