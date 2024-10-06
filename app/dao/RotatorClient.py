import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 4532)
sock.connect(server_address)

try:
    command = 'P 135 10' #dummy command TODO: input from dump1090
    sock.sendall(command.encode('utf8'))

    #response = sock.recv(1024)
    #print('Received:', response.decode('utf8'))

finally:
    sock.close()
