import os
import random
import sys
from socket import *
import pickle
import select

M_DATA = 0
M_ACK = 1

STATE_SEND = 1
STATE_WAIT = 2
STATE_RECV = 3
STATE_TIMEOUT = 4
STATE_END = 5

chunkSize = 1024
dgramSize = chunkSize + sys.getsizeof(int) * 2  # 2 ints for the header

ss = socket(AF_INET, SOCK_DGRAM)
receiverAddr = ()

#TODO: Remove this
senderAddr = ("127.0.0.1", 10000)
receiverAddr = ("127.0.0.1", 10001)


def sendDatagram(msg, sock, address):
    # msg is a byte array ready to be sent
    # Generate random number in the range of 1 to 10
    rand = random.randint(1, 10)

    # 20% of loss probability TODO change this number
    if rand > 0:
        sock.sendto(msg, address)


def waitForReply(uSocket, timeOutInSeconds):
    rx, tx, er = select.select([uSocket], [], [], timeOutInSeconds)
    # waits for data or timeout
    if not rx:
        return False
    else:
        return True


def make_pkt(data, pktNum):
    pkt = pickle.dumps((M_DATA, pktNum, data))  # 0 indicates that it is a data packet
    return pkt


def rdt_send(data, pktNum):
    pkt = make_pkt(data, pktNum)
    sendDatagram(pkt, ss, receiverAddr)


def main():

    global receiverAddr

    if len(sys.argv) != 7:
        print("Wrong number of arguments.")
        sys.exit(6969)

    senderIP = sys.argv[1]
    senderPort = int(sys.argv[2])

    #TODO: uncomment this
    """ 
    receiverIP = sys.argv[3]
    receiverPort = int(sys.argv[4])
    receiverAddr = (receiverIP, receiverPort)
    """

    fileName = sys.argv[5]
    windowSize = int(sys.argv[6])

    if senderPort < 1024 or senderPort > 65535:
        print("Incorrect Sender Port number.")
        sys.exit(69420)

    """
    if receiverPort < 1024 or receiverPort > 65535:
        print("Incorrect Receiver Port number.")
        sys.exit(69421)
    """

    if windowSize < 1 or windowSize > 10:
        print("Invalid window size.")
        sys.exit(69422)

    print("Sender is running.")

    #TODO: uncomment this
    #ss.bind((senderIP, senderPort))

    #TODO: Remove this
    ss.bind(senderAddr)


    pktNum = 0

    state = STATE_SEND
    file = open("./senderFiles/" + fileName, 'rb')

    while True:
        if state == STATE_SEND:
            file.seek(pktNum * chunkSize)
            data = file.read(chunkSize)

            if not data:
                state = STATE_END
                continue

            rdt_send(data, pktNum)
            state = STATE_WAIT

        elif state == STATE_WAIT:
            if waitForReply(ss, 1):
                state = STATE_RECV
            else:
                state = STATE_TIMEOUT

        elif state == STATE_RECV:
            reply, trash = ss.recvfrom(dgramSize)
            reply = pickle.loads(reply)
            if int(reply[0]) == M_ACK:  # ack
                pktNum = int(reply[1])
            else:
                print("Error: received a data packet instead of an ack.")
            state = STATE_SEND

        elif state == STATE_TIMEOUT:
            state = STATE_SEND

        elif state == STATE_END:
            ss.sendto(pickle.dumps((M_DATA, -1, b'')), receiverAddr)
            print("File transfer complete.")
            break

    file.close()
    ss.close()


if __name__ == "__main__":
    main()
