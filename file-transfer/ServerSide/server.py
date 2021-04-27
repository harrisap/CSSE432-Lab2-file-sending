import socket
import sys
import tqdm
import os

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
            while True:
                data = connection.recv(1024).decode() # max 1024 bytes to receive at once
                if not data: # something went wrong, or no more data. exit the loop for this connection.
                    break
                data_stripped = data.strip()
                if data_stripped == "cease":
                    data = "CLOSE_ME"
                    connection.send("Shutting down".encode())
                    break
                elif data_stripped.find("iWant ", 0) == 0: # command words must be at the very start
                    print("calling iWant")
                elif data_stripped.find("uTake ", 0) == 0:
                    print("calling uTake")
                    path = data_stripped[6::]
                    print(path)

                    connection.send("DATAI".encode())

                    # receive the file infos
                    # receive using client socket, not server socket
                    received = connection.recv(BUFFER_SIZE).decode()
                    filename, filesize = received.split(SEPARATOR)
                    # remove absolute path if there is
                    filename = os.path.basename(filename)
                    # convert to integer
                    filesize = int(filesize)

                    connection.send("YRECV".encode())

                    receive_file(filename, filesize, connection)


                else:
                    print("unrecognized")
                

                print("\tFrom " + str(client_address) +": " + str(data))
                data = str(data).upper()
                connection.send(data.encode())
        except ConnectionResetError:
            print("Client connection was reset - disconnecting them")
            connection.close()


        connection.close()
        print("Goodbye " + str(client_address))



def receive_file(filename, filesize, client_socket):
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    # close the client socket
    # client_socket.close()
    # # close the server socket
    # s.close()


if __name__ == '__main__':
    server_program()