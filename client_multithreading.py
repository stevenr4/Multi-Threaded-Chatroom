__author__ = 'spex'

# We need to have Sockets and Threads to make this chat server work
import socket, thread               

# The host variable will be a manual string input (improve users?)
host = raw_input("Enter the IP address of the server\n> ")
# Now a username for the user
name = raw_input("What would you like your username to be?\n> ")

# We just started, so let's let the application know that we are running
running = True

# This function is going to be a thread on its own
def listenAndPrint(conn):

    # Get the global 'running' variable so we can use it in this thread
    global running

    # Now we will start the whil loop for this thread.
    # This while loop will listen for incoming data and print whatever comes trough the socket
    while running:

        # There are bugs when there is a un-intentional disconneciton from the server, so we handle those with a try
        try:

            # This conn(ection).recv(4056) will wait till some data comes through the connection and then apply it to 'printString'
            printString = conn.recv(4056)

            # If the printstring started with the code character '_', that is my code for disconnection from the server
            if printString.startswith('_'):
                print "You have been disconnected from the server."
                running = False

            # Otherwise, we want to print out the data, sometimes the socket hangs up giving me an infinite  amount of '\n' characters, That means disconneciton
            elif len(printString) < 3:
                print "BUG! It's not suppose to reach this print statement!!!!"
                for char in printString:
                    print ord(char) + "LKSDJ"
                print type(printString)
                running = False

            # If it's not an intentional disconnection or the 'hangup' bug, then we know it's a valid message and we print that stringout
            else:
                print printString

        # This except happens when there is a disconnection that wasn't intended
        except:
            print "You have lost connection from the server."
            running = False


# This function waits for user input and sends it through the connection
def inputAndSend(conn):

    # Get the running variable fromt he global thread
    global running

    # Start the main loop that will continue until the connection is severed
    while running:

        # Sometimes, the connection bugs out when it disconnects unintentionally
        try:
            # Get the string from the raw input
            sendString = raw_input()
            # Send the user's string through the socket
            conn.send(sendString)

        # This error occurs when the message-sending breaks
        except:
            print "Message failed to send."
            running = False


# We create the socket
s = socket.socket()

# This is the hard-coded static port number, it's the same with the SERVER
port = 9002

# Print that we are going to attempt to connect to the host
print "Attempting to connect to " + host
s.connect((host, port))

# Let the user know we successfully connected to the host
print "Connected! Type '\\help' for a list of commands"

# Send to the server the person's username (The server waits for this data when connection starts)
s.send(name)

# Start both sending and receiving threads
thread.start_new_thread(listenAndPrint,(s,))
thread.start_new_thread(inputAndSend,(s,))


# Let the threads run and have them decide when the connection is done
while running:
    pass

# Close the connections (we are done)
s.close()

# Say goodnight to the user
print "\nGoodnight\n"