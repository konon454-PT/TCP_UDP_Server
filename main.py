import socket
import sys
import re
import logging

# Required variables
serverPort = 4367
serverName = ''
message = 'whatamess'
LogFilename = ''

# Required execution flags
checkIP = True
checkPort = True
isServer = False
isTCP = True
isUDP = False
TCPflag = False
UDPflag = False
isLogSc = False
isLogFile = False

# Logger object
logger = logging.getLogger(__name__)


def logging_config():
    global isLogSc
    global isLogFile
    logger.setLevel(logging.INFO)
    if not isLogSc and not isLogFile:
        isLogSc = True
        isLogFile = False
    if isLogSc:
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_format = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
    if isLogFile:
        f_handler = logging.FileHandler(LogFilename)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)


def check_flags():
    # Required because of incorrect working some 'if' statements
    global isLogFile
    global isLogSc
    global isUDP
    global isTCP
    global isServer
    global LogFilename
    global serverPort
    global serverName
    global checkIP
    global checkPort
    global TCPflag
    global UDPflag

    argvarr = sys.argv[:]

    if len(argvarr) == 1:
        logging.critical('Run format: python <filename.py> <host> <port>'
                         ' [-s] [-t | -u] [-o | -f <file>]')
        sys.exit(1)

    for i in argvarr[3:]:
        if isLogFile:
            if re.match('-', i):
                logging.error('Expected filename after -f, not flag!')
                sys.exit(1)
            LogFilename = i
            isLogFile = False  # Чтобы больше не проверялось в цикле
        if i == '-s':
            isServer = True
        elif i == '-u':
            UDPflag = True
        elif i == '-t':
            TCPflag = True
        elif i == '-o':
            isLogSc = True
        elif i == '-f':
            isLogFile = True
        elif i == '-ip':
            checkIP = False
        elif i == '-port':
            checkPort = False

    if isLogFile:
        logging.error('Missing log filename')
        sys.exit(1)

    if LogFilename != '':
        isLogFile = True

    if TCPflag and UDPflag:
        logging.error("TCP and UDP can't be used at the same time")
        sys.exit(1)
    elif TCPflag:
        isTCP = True
        isUDP = False
    elif UDPflag:
        isTCP = False
        isUDP = True

    if checkIP:
        try:
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', argvarr[1]) and len(argvarr[1]) <= 15:
                pass
            else:
                logging.error('IP format checking failed. If you are sure that the entered IP is correct, '
                              'run the program with the -ip flag')
                sys.exit(1)
        except IndexError:
            logging.critical('IP address not found')
            sys.exit(1)
        except Exception:
            logging.critical('Exception info:', exc_info=True)
            sys.exit(1)

    if checkPort:
        try:
            if 1024 <= int(argvarr[2]) <= 49151:
                pass
            else:
                logging.error('Port checking failed. If you are sure that the entered port is correct, '
                              'run the program with the -port flag')
                sys.exit(1)
        except IndexError:
            logging.critical('Port not found')
            sys.exit(1)
        except ValueError:
            logging.critical('Port should be integer value')
            sys.exit(1)
        except Exception:
            logging.critical('Exception info:', exc_info=True)
            sys.exit(1)


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


if __name__ == '__main__':
    check_flags()
    logging_config()
    print(isServer, isTCP, isUDP, isLogSc, isLogFile, checkIP, checkPort)
    logger.info('It works!')


