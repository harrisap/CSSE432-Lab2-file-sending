import socket
import sys
import os
import tqdm
import os.path
from os import path

help_msg = "Valid commands are: iWant, uTake, help\nType 'exit' to exit."

SEPARATOR = "<SEPARATOR>"

BUFFER_SIZE = 1024


def client_program():
    if(len(sys.argv) != 3):
        print("Usage: python client.py <server_(IP)_address> <server_port_number>")
        sys.exit()

    port = int(sys.argv[2])
    server_addr = (sys.argv[1], port)

    print("Will connect to " + str(server_addr))
    print(help_msg)

    while True:
        message = input("> ")
        message = message.strip()
        if message == 'exit':
            break
        elif message == 'help':
            print(help_msg)
        else:
            command = message[0:5]

            try:
                client_socket = None

                if(command == "uTake"):
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect(server_addr)
                    handleUTake(message, client_socket)

                elif (command == "iWant"):
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect(server_addr)
                    handleIWant(client_socket, message)

                else:
                    print("That just ain't right!")

                if client_socket:
                    client_socket.close()
            except Exception as e:
                print("Could not connect to server to run your command!")
                print(e)


def handleUTake(message, client_socket):
    if(path.exists(message[6:])):

        # file exists, send message

        filename = message[6:]
        filesize = os.path.getsize(filename)

        client_socket.send(message.encode())

        response = client_socket.recv(1024).decode()

        if(str(response) == "DATAI"):

            # server is requesting data info

            # print("Server waiting for file information...")

            client_socket.send(
                f"{filename}{SEPARATOR}{filesize}".encode())

            response = client_socket.recv(1024).decode()

            if(str(response) == "YRECV"):

                # print("Server accepted transfer!")
                print("Transferring file from Willis to Server...")

                sendFile(filename, client_socket)

            else:
                print("Internal server error [1]")

        else:
            print("Internal server error [2]")

    else:
        print("Willis, you idiot, you don't even have that file!\n(File not found) cwd is:")
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
        print("Failure:  What you talkin' bout Willis?  I ain't seen that file nowhere!")
        print("(Check if you got the file path correct)")


def sendFile(filename, client_socket):
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file

            bytes_read = f.read(BUFFER_SIZE)

            if not bytes_read:
                # file transmission is finished
                print("File sent! Thanks Willis!")
                break

            client_socket.sendall(bytes_read)


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
