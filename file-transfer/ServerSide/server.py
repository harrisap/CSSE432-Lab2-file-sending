import socket
import sys
import tqdm
import os
import os.path
from os import path

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def server_program():
    # get the hostname and print it
    host = socket.gethostname()
    print("Host Name: " + str(host))

    if(len(sys.argv) != 2):
        print("Usage is python server.py <port number>")
        sys.exit()

    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP

    server_socket.bind((host, port)) # note - takes a tuple

    print(f"Opened server on port {port}. I am {host}")

    server_socket.listen(2) # buffer 2 incoming requests

    data = "just_opened"
    while data != "CLOSE_ME":
        connection, client_address = server_socket.accept()
        print("Connection from" + str(client_address))

        try:
            # receive data. we will call break when the connection closes
            # while True:
            data = connection.recv(1024).decode() # max 1024 bytes to receive at once
            print("==GOT==")
            print(data)
            print("=======")
            if not data: # something went wrong, or no more data. exit the loop for this connection.
                break
            data_stripped = data.strip()
            if data_stripped == "cease":
                data = "CLOSE_ME"
                connection.send("Shutting down".encode())
                break
            elif data_stripped.find("iWant ", 0) == 0: # command words must be at the very start
                handleIWant(data_stripped, connection) # file does not exist
            elif data_stripped.find("uTake ", 0) == 0:
                handleUTake(data_stripped, connection)
            else:
                print("unrecognized data format")
        except ConnectionResetError:
            print("Client connection was reset - disconnecting them")
            connection.close()
        except ConnectionAbortedError:
            print("Client connection was aborted - disconnecting them")
            connection.close()

        connection.close()
        print("Goodbye " + str(client_address))

def handleUTake(data_stripped, connection):
    filePath = data_stripped[6::]
    print("calling uTake. Path is: " + filePath)

    connection.send("DATAI".encode())
    print("Sent DATAI")

    # receive the file infos
    # receive using client socket, not server socket
    received = connection.recv(BUFFER_SIZE).decode()
    print("Got fileinfo:")
    print(received)
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    connection.send("YRECV".encode())
    print("Sent YRECV. awaiting file data")

    receiveFile(filename, filesize, connection)

def handleIWant(data_stripped, connection):
    filePath = data_stripped[6::]
    filePath = f"store/{filePath}"
    print("calling iWant. Path is: " + filePath)

    if(path.exists(filePath)):
        print("File exists, sending FILEE")
        connection.send("FILEE".encode()) # file exists

        response = connection.recv(1024).decode()
        if(str(response) == "DATAI"):
            print("Got DATAI - sending file info")

            filename = filePath
            filesize = os.path.getsize(filename)
            connection.send(f"{filename}{SEPARATOR}{filesize}".encode())

            response = connection.recv(1024).decode()
            if(str(response) == "YRECV"):
                print("Got YRECV - sending file contents")

                sendFile(filename, connection)
                connection.close()
            else:
                print("Client did not send YRECV")

        else:
            print("Client did not send DATAI")
    else:
        print("Requested file " + filePath + " does not exist, sending FILEN")
        connection.send("FILEN".encode()) # file does not exist

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

def receiveFile(filename, filesize, client_socket):
    with open(filename, "wb") as f:
        while True:

            bytes_read = client_socket.recv(BUFFER_SIZE)

            if not bytes_read:
                # nothing received
                print("Finished recv")
                break

            f.write(bytes_read)
        
        print("Finished recv")

if __name__ == '__main__':
    server_program()