# Names: Kevin Mcnulty, Nadia Rahbany, Juli Shinozuka, and Andrew Shiraki
# Date: June 16, 2022
# Title: Chat Server Program (from PA3EC)
# Description: This is a TCP chat server program that uses threads with two client
# programs that connect to it.  Both client programs must be connected before the
# server sends a message to both clients that they have been connected to the
# server.  The server then waits on both client threads for incoming messages
# which are sent to the other client.  A thread is closed if the exiting word
# "Bye" is sent in one of the messages.  After both client threads close,
# the server displays a final message, waits 2 seconds, and terminates.

# socket module used for network communications
from socket import *
# for threading 2 clients
import threading
# used for pausing before terminating program at end
import time

"""
This function is used by threads processes of two connected clients so that
they can function in parallel.
"""
def thread_function(cIndex, cList, clients):
    # Send acknowledgement to clients that they are connected
    sMessage = 'Client {} connected'.format(cList[cIndex])
    clients[cIndex].send(sMessage.encode())

    while True:
        try:
            rMessage = clients[cIndex].recv(1024).decode()
            if rMessage:
                sMessage = 'Client {}: {}'.format(cList[cIndex], rMessage)
                for c in clients:
                    if c != clients[cIndex]:
                        c.send(sMessage.encode())
                print(sMessage)
            if rMessage.lower() == 'bye':
                break
        except:
            break

    for c in clients:
        c.close()

"""
This is the main function.
"""
def Main():
    threadCount = 0     # counter used to know which client connected first.  0 = X, 1 = Y
    clientList = ['X', 'Y']    # used to pass client char to its thread
    clients = []

    serverPort = 12000                              # set listening port
    serverSocket = socket(AF_INET, SOCK_STREAM)     # create TCP socket with IPv4

    serverSocket.bind(('', serverPort))

    serverSocket.listen(1)
    print('The server is waiting to receive 2 connections....\n')

    # Create thread processes using accepted connections for max connections (2)
    for threadCount in range(2):
        connectionSocket, addr = serverSocket.accept()
        clients.append(connectionSocket)

        # Display on server the client connections and create threads
        if threadCount == 0:
            print('Accepted first connection, calling it client {}'.format(clientList[threadCount]))
            xThread = threading.Thread(target=thread_function, args=(threadCount, clientList, clients))
            threadCount += 1
        else:
            print('Accepted second connection, calling it client {}\n'.format(clientList[threadCount]))
            yThread = threading.Thread(target=thread_function, args=(threadCount, clientList, clients))
            threadCount += 1

    # Start thread processes after max number of threads are received (2)
    print('Waiting to receive messages from client X and client Y....\n')
    xThread.start()
    yThread.start()

    # wait for client threads to terminate before continuing with main
    xThread.join()
    yThread.join()

    print('\nWaiting a bit for clients to close their connections')
    time.sleep(2)
    print('Done.')
    serverSocket.close()

"""
Start the program by running Main()
"""
if __name__ == '__main__':
    Main()
