"""TCP/UDP Client-Server application"""
import socket
import sys
import re
import logging

# Required variables
SERVER_PORT = 4367
SERVER_NAME = ''
MESSAGE = 'whatamess'
STOP_MESSAGE = 'stop'
LOG_FILENAME = ''

# Required execution flags
CHECK_IP = True
CHECK_PORT = True
IS_SERVER = False
IS_TCP = True
IS_UDP = False
TCP_FLAG = False
UDP_FLAG = False
IS_LOG_SC = False
IS_LOG_FILE = False

# Logger object
logger = logging.getLogger(__name__)


def logging_config():
    """ Configuring logging module (Doesn't config when checking flags) """
    global IS_LOG_SC
    global IS_LOG_FILE
    logger.setLevel(logging.INFO)
    if not IS_LOG_SC and not IS_LOG_FILE:
        IS_LOG_SC = True
        IS_LOG_FILE = False
    if IS_LOG_SC:
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_format = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
    if IS_LOG_FILE:
        f_handler = logging.FileHandler(LOG_FILENAME)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)


def check_flags():
    """ Checking input flags """
    # Required because of incorrect working some 'if' statements. Try delete them if don't believe:)
    global IS_LOG_FILE
    global LOG_FILENAME
    global CHECK_IP
    global CHECK_PORT
    global TCP_FLAG
    global UDP_FLAG
    global IS_LOG_SC
    global IS_UDP
    global IS_TCP
    global IS_SERVER
    global SERVER_PORT
    global SERVER_NAME

    argvarr = sys.argv[:]

    if len(argvarr) == 1:
        logging.critical('Run format: python <filename.py> <host> <port>'
                         ' [-s] [-t | -u] [-o | -f <file>]')
        sys.exit(1)

    for i in argvarr[3:]:
        if IS_LOG_FILE:
            if re.match('-', i):
                logging.error('Expected filename after -f, not flag!')
                sys.exit(1)
            LOG_FILENAME = i
            IS_LOG_FILE = False  # Чтобы больше не проверялось в цикле
        if i == '-s':
            IS_SERVER = True
        elif i == '-u':
            UDP_FLAG = True
        elif i == '-t':
            TCP_FLAG = True
        elif i == '-o':
            IS_LOG_SC = True
        elif i == '-f':
            IS_LOG_FILE = True
        elif i == '-ip':
            CHECK_IP = False
        elif i == '-port':
            CHECK_PORT = False

    if IS_LOG_FILE:
        logging.error('Missing log filename')
        sys.exit(1)

    if LOG_FILENAME != '':
        IS_LOG_FILE = True

    if TCP_FLAG and UDP_FLAG:
        logging.error("TCP and UDP can't be used at the same time")
        sys.exit(1)
    elif TCP_FLAG:
        IS_TCP = True
        IS_UDP = False
    elif UDP_FLAG:
        IS_TCP = False
        IS_UDP = True

    if CHECK_IP:
        try:
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', argvarr[1]) and\
                    len(argvarr[1]) <= 15:
                SERVER_NAME = argvarr[1]
            else:
                logging.error('IP format checking failed. If you are sure that the '
                              'entered IP is correct, '
                              'run the program with the -ip flag')
                sys.exit(1)
        except IndexError:
            logging.critical('IP address not found')
            sys.exit(1)
        except Exception:
            logging.critical('Exception info:', exc_info=True)
            sys.exit(1)
    else:
        SERVER_NAME = argvarr[1]

    if CHECK_PORT:
        try:
            if 1024 <= int(argvarr[2]) <= 49151:
                SERVER_PORT = int(argvarr[2])
            else:
                logging.error('Port checking failed. If you are sure '
                              'that the entered port is correct, '
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
    else:
        SERVER_PORT = int(argvarr[2])


def udp_client(messg):
    """ UDP Client """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logger.info('UDP Client socket has been created')
    client_socket.sendto(messg.encode('utf-8'), (SERVER_NAME, SERVER_PORT))
    srv_addr = SERVER_NAME + ":" + str(SERVER_PORT)
    logger.info('Message has been sent to %s', srv_addr)
    receivedmessg = client_socket.recvfrom(2048)
    logger.info('Message has been received')
    receivedmessg = receivedmessg[0].decode('utf-8')
    client_socket.close()
    logger.info('UDP Client socket has been closed')
    return receivedmessg


def udp_server():
    """ UDP Server """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logger.info('UDP Server socket has been created')
    server_socket.bind((SERVER_NAME, SERVER_PORT))
    logger.info('UDP Server socket has been bound to port %d', SERVER_PORT)
    while 1:
        control_messg, client_addr = server_socket.recvfrom(2048)
        if control_messg.decode('utf-8') == MESSAGE:
            logger.info('Message has been received')
            cl_addr = str(client_addr[0]) + ':' + str(client_addr[1])
            server_socket.sendto(cl_addr.encode('utf-8'), client_addr)
            logger.info('Message has been sent to %s', cl_addr)
        if control_messg.decode('utf-8') == STOP_MESSAGE:
            server_socket.sendto('Server has been stopped'.encode('utf-8'), client_addr)
            server_socket.close()
            logger.info('UDP Server socket has been closed')
            break


def tcp_client(messg):
    """ TCP Client """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info('TCP Client socket has been created')
    client_socket.connect((SERVER_NAME, SERVER_PORT))
    srv_addr = SERVER_NAME + ":" + str(SERVER_PORT)
    client_socket.send(messg.encode('utf-8'))
    logger.info('Message has been sent to %s', srv_addr)
    receivedmessg = client_socket.recv(1024)
    logger.info('Message has been received')
    client_socket.close()
    logger.info('TCP Client socket has been closed')
    return receivedmessg.decode('utf-8')


def tcp_server():
    """ TCP Server """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info('TCP Server socket has been created')
    server_socket.bind((SERVER_NAME, SERVER_PORT))
    logger.info('TCP Server socket has been bound to port %d', SERVER_PORT)
    server_socket.listen(1)
    while 1:
        connection_socket, addr = server_socket.accept()
        control_msg = (connection_socket.recv(1024)).decode('utf-8')
        if control_msg == MESSAGE:
            logger.info('Message has been received')
            cl_addr = str(addr[0]) + ':' + str(addr[1])
            connection_socket.send(cl_addr.encode('utf-8'))
            logger.info('Message has been sent to %s', cl_addr)
            connection_socket.close()
            logger.info('TCP Connection socket has been closed')
        if control_msg == STOP_MESSAGE:
            logger.info('Message has been received')
            cl_addr = str(addr[0]) + ':' + str(addr[1])
            connection_socket.send('Server has been stopped'.encode('utf-8'))
            logger.info('Message has been sent to %s', cl_addr)
            connection_socket.close()
            logger.info('TCP Connection socket has been closed')
            logger.info('Server stop')
            break


if __name__ == '__main__':
    check_flags()
    logging_config()
    if IS_SERVER:
        if IS_UDP:
            udp_server()
        if IS_TCP:
            tcp_server()
    else:
        MESSAGE_TO_RECEIVE = ''
        code = input('Do you want to stop the server? ')
        if code in ('y', 'Y'):
            MESSAGE_TO_RECEIVE = STOP_MESSAGE
        else:
            MESSAGE_TO_RECEIVE = MESSAGE
        if IS_UDP:
            print(udp_client(MESSAGE_TO_RECEIVE))
        if IS_TCP:
            print(tcp_client(MESSAGE_TO_RECEIVE))
