from socket import *
import pickle
import select
import sys
import random


def sendDatagram (msg, sock, address):
    # msg is a byte array ready to be sent
    # Generate random number in the range of 1 to 10
    rand = random.randint(1, 10)

    # 20% of loss probability
    if rand > 2:
        sock.sendto(msg, address)


def waitForReply( uSocket, timeOutInSeconds ):
    rx, tx, er = select.select([uSocket], [], [], timeOutInSeconds)
    # waits for data or timeout
    if not rx:
        return False
    else:
        return True


def main():
    # Check number of arguments
    if len(sys.argv) != 4:
        print("Wrong number of arguments.")
        sys.exit(6969)

    port = int(sys.argv[2])  # port number
    serverAddressPort = (sys.argv[1], port)  # server IP and port
    fileName = sys.argv[3]  # name of the file in the receiver

    if port < 1024 or port > 65535:
        print("Incorrect port number.")
        sys.exit(69420)

    print("Client is running.")

    rs = socket(AF_INET, SOCK_DGRAM)

    # file open
    file = open("./" + fileName, 'wb')

    offset = 0

    while True:
        if waitForReply(rs, 1):
            break

    file.close()
    rs.close()


if __name__ == "__main__":
    main()