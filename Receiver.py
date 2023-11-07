from socket import *
import pickle
import select
import sys
import random


STATE_SEND = 1
STATE_WAIT = 2
STATE_RECV = 3
STATE_END = 4

TIMEOUT = 1  # seconds
chunkSize = 1024
dgramSize = chunkSize + sys.getsizeof(int) * 2  # 2 ints for the header

rs = socket(AF_INET, SOCK_DGRAM)
senderAddr = ()


def sendDatagram(msg, sock, address):
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


def sortFunc(x):
    return x[0]


def main():
    # Check number of arguments
    global senderAddr

    if len(sys.argv) != 4:
        print("Wrong number of arguments.")
        sys.exit(6969)

    port = int(sys.argv[2])  # port number

    fileName = sys.argv[3]  # name of the file in the receiver

    if port < 1024 or port > 65535:
        print("Invalid port number.")
        sys.exit(69420)

    rs.bind((sys.argv[1], port))


    print("Receiver is running.")

    # file open
    file = open("./receiverFiles/" + fileName, 'wb')

    writtenPKT = 0  # number of packets written to the file
    confirm = -1
    state = STATE_WAIT
    ended = False

    waitList = []  # list of packets that arrived out of order

    while True:

        if state == STATE_WAIT:
            if not ended:
                if waitForReply(rs, TIMEOUT):
                    state = STATE_RECV
            else:
                if waitForReply(rs, TIMEOUT * 5):
                    state = STATE_RECV
                else:
                    print("File transfer complete.")
                    break


        elif state == STATE_RECV:
            reply, sAddr = rs.recvfrom(dgramSize)

            if senderAddr == ():
                senderAddr = sAddr

            if senderAddr != sAddr:
                print("Error: Received a packet from a different sender.")
                continue

            reply = pickle.loads(reply)  # (status, pktNum, data)
            pktNum = int(reply[1])

            if reply[0] != 0:
                print("Error: Received a non data packet.")
                continue

            if pktNum == -1:
                state = STATE_END
                continue

            if pktNum == confirm + 1:
                file.write(reply[2])
                confirm += 1

                # Verify if there are packets in the buffer that can be written
                if len(waitList) != 0:
                    counter = 0
                    for i in range(0, len(waitList) - 1):
                        if waitList[i-counter][0] == confirm + 1:
                            file.write(waitList[i-counter][1])
                            confirm += 1
                            waitList.pop(i-counter)
                            counter += 1

            elif pktNum > confirm + 1:
                # save in buffer to write later
                waitList.append((pktNum, reply[2]))
                waitList.sort(reverse=False, key=sortFunc)

            state = STATE_SEND

        elif state == STATE_SEND:
            # send ack
            ack = pickle.dumps((1, confirm))
            sendDatagram(ack, rs, senderAddr)
            state = STATE_WAIT

        elif state == STATE_END:  # Special treatment for the last packet
            # send ack
            ack = pickle.dumps((1, -1))
            sendDatagram(ack, rs, senderAddr)
            ended = True
            state = STATE_WAIT






    file.close()
    rs.close()


if __name__ == "__main__":
    main()


