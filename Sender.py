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

size = 1024

ss = socket(AF_INET, SOCK_DGRAM)


def sendDatagram (msg, sock, address):
    # msg is a byte array ready to be sent
    # Generate random number in the range of 1 to 10
    rand = random.randint(1, 10)

    # 20% of loss probability
    if rand > 2:
        sock.sendto(msg, address)


def waitForReply(uSocket, timeOutInSeconds):
    rx, tx, er = select.select([uSocket], [], [], timeOutInSeconds)
    # waits for data or timeout
    if not rx:
        return False
    else:
        return True


def make_pkt(data):
    pkt = pickle.dumps((M_DATA, npkt, data))  # 0 indicates that it is a data packet
    return pkt


def rdt_send(data):
    pkt = make_pkt(data)
    sendDatagram(pkt, ss, (receiverIP, receiverPort))


def main():
    state = STATE_SEND
    file = open("./" + fileName, 'rb')

    while True:
        if state == STATE_SEND:
            data = file.read(size)

            if not data:
                state = STATE_END
                break

            rdt_send(data)
            state = STATE_WAIT

        elif state == STATE_WAIT:
            if waitForReply(ss, 1):
                state = STATE_RECV
            else:
                state = STATE_TIMEOUT

        elif state == STATE_RECV:
            reply, trash = ss.recvfrom(size)
            reply = pickle.loads(reply)
            if int(reply[0]) == M_ACK:  # ack
                npkt += 1
            else:
                print("Error: received a data packet instead of an ack.")
            state = STATE_SEND

        elif state == STATE_TIMEOUT:
            state = STATE_SEND


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Wrong number of arguments.")
        sys.exit(6969)

    senderIP = sys.argv[1]
    senderPort = int(sys.argv[2])

    receiverIP = sys.argv[3]
    receiverPort = int(sys.argv[4])

    fileName = sys.argv[5]
    window = int(sys.argv[6])

    if senderPort < 1024 or senderPort > 65535:
        print("Incorrect Sender Port number.")
        sys.exit(69420)

    if receiverPort < 1024 or receiverPort > 65535:
        print("Incorrect Receiver Port number.")
        sys.exit(69421)

    if window < 1 or window > 10:
        print("Incorrect window size.")
        sys.exit(69422)

    print("Sender is running.")

    ss.bind((senderIP, senderPort))

    npkt = 0

    main()
