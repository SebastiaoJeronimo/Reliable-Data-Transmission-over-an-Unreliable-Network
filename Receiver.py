from socket import *
import pickle
import select
import sys
import random


STATE_SEND = 1
STATE_WAIT = 2
STATE_RECV = 3
STATE_END = 4

chunkSize = 1024
dgramSize = chunkSize + sys.getsizeof(int) * 2  # 2 ints for the header

rs = socket(AF_INET, SOCK_DGRAM)
senderAddr = ()

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

    # TODO: uncomment this
    #rs.bind((sys.argv[1], port))

    #TODO: Remove this
    rs.bind(receiverAddr)

    print("Receiver is running.")

    # file open
    file = open("./receiverFiles/" + fileName, 'wb')

    offset = 0
    writtenPKT = 0
    confirm = -1
    state = STATE_WAIT

    while True:
        if state == STATE_WAIT:
            if waitForReply(rs, 1):
                state = STATE_RECV

        elif state == STATE_RECV:
            print("Receiving packet...")
            reply, sAddr = rs.recvfrom(dgramSize)


            #if senderAddr == ():
            #    senderAddr = sAddr

            if senderAddr != sAddr:
                print("Error: Received a packet from a different sender.")
                continue

            reply = pickle.loads(reply)  # (status, pktNum, data)
            pktNum = int(reply[1])
            print("Packet received: ", pktNum, ".")

            if reply[0] != 0:
                print("Error: Received a non data packet.")
                continue

            if pktNum == -1:
                state = STATE_END
                continue

            if pktNum == writtenPKT:
                print("Writing packet number ", pktNum, ".")
                file.write(reply[2])
                print("Packet written.")
                offset += len(reply[2])
                writtenPKT += 1
                """ 
                # Verify if there are packets in the buffer that can be written
                """
                state = STATE_SEND
                confirm = writtenPKT

            else:
                if pktNum < writtenPKT:
                    # resend ack
                    state = STATE_SEND
                    confirm = writtenPKT

                """
                else:
                    #add to buffer and wait for the rest of the packets
                    buffer.append((pktNum, reply[2]))
                    state = STATE_SEND
                    confirm = pktNum
                """

        elif state == STATE_SEND:
            # send ack
            ack = pickle.dumps((1, confirm))
            sendDatagram(ack, rs, senderAddr)
            state = STATE_WAIT

        elif state == STATE_END: #TODO fix this
            # send ack
            ack = pickle.dumps((1, confirm))
            sendDatagram(ack, rs, senderAddr)
            print("File transfer complete.")
            break

    file.close()
    rs.close()


if __name__ == "__main__":
    main()


