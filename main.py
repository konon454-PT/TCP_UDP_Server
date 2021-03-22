import socket
import sys
import re

# Required constants
serverPort = 4367
serverName = ''
message = 'whatamess'
LogFilename = ''

# Required execution flags
isIPCorrect = False
isPortCorrect = False
isServer = False
isTCP = False
isUDP = False
isLogSc = False
isLogFile = False


def debug():
    check_flags()
    print(isIPCorrect, isPortCorrect, isServer, isTCP, isUDP, isLogSc, isLogFile)


def check_flags():
    global isLogFile
    global isLogSc
    global isUDP
    global isTCP
    global isServer
    global isPortCorrect
    global isIPCorrect
    global LogFilename
    global serverPort
    global serverName

    argvarr = sys.argv[:]
    # print(argvarr)
    if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', argvarr[1]) and len(argvarr[1]) <= 15:
        isIPCorrect = True
        print("IP is correct")
        # LOG - IP format checking: correct
    else:
        print("IP is incorrect")
        # LOG - IP format checking: error

    # ADD CHECK IF PORT IS INTEGER
    if 1024 <= int(argvarr[2]) <= 49151:
        isPortCorrect = True
        print("Port is correct")
        # LOG - Port format checking: correct
    else:
        print("Port is incorrect")
        # LOG - Port format checking: error

    for i in argvarr[3:]:
        if isLogFile:
            if re.match('-', i):
                print('Expected filename, not flag!')
                # LOG - Expected filename, not flag!
            LogFilename = i
            isLogFile = False  # Чтобы больше не проверялось в цикле
            # LOG - Log filename: on
        if i == '-s':
            isServer = True
            # LOG - Server Mode: on
        if i == '-t':
            isTCP = True
            # LOG - TCP Mode: on
        if i == '-u':
            isUDP = True
            # LOG - UDP Mode: on
        if i == '-o':
            isLogSc = True
            # LOG - Log in stdout: on
        if i == '-f':
            isLogFile = True
            # LOG - Log in file: on

    if LogFilename != '':
        isLogFile = True

    if (isTCP and isUDP) or (not isTCP and not isUDP):
        print("Incorrect TCP/UDP mode")


def udp_client():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.sendto(message.encode('utf-8'), (serverName, serverPort))
    receivedMessage = clientSocket.recvfrom(2048)
    receivedMessage = receivedMessage.decode('utf-8')
    clientSocket.close()
    return receivedMessage


def udp_server():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print("The server is ready to receive")
    while 1:
        controlMessage, clientAddress = serverSocket.recvfrom(2048)
        if controlMessage.decode('utf-8') == message:
            serverSocket.sendto(clientAddress.encode('utf-8'), clientAddress)


debug()
