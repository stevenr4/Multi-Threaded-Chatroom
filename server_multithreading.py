__author__ = 'spex'

# We need the Socket for connecting, Thread for multithreading, and Time for timestamping the user's messages
import socket, thread, time               # Import socket module


# This variable lets all the threads know that the server is still running
running = True

# This is a global variable that has the list of all connected users
list_of_users = []

# This function just returns the current time in a tuple
def getTime():
    #print "Getting Time"
    tmpCurrentTime = time.localtime(time.time())
    return (tmpCurrentTime[3],tmpCurrentTime[4],tmpCurrentTime[5])


# This is the class for the connected user object
class User(object):

    # Each user has a Connection, Address, and a (NON-UNIQUE) username
    def __init__(self,conn, addr, name):
        self.conn = conn
        self.addr = addr
        self.name = name
        self.timeLogin = getTime()
        self.timeLastPost = getTime()
        pass

    # Function to send a message to that specific user
    def send(self, sendString):
        self.conn.send(sendString)

    # Funciton to get the 'SendString' (The formatted string for when that user sent something)
    def getSendString(self, sendString):
        return ("%d:%d:%d - [" + self.name + "] > " + sendString) % (self.timeLastPost[0],self.timeLastPost[1],self.timeLastPost[2])

    # Self Explanitory
    def setName(self,newName):
        self.name = newName

    # This function returns a string that contains all the data for a specific user
    def getDataString(self):
        return ("[" + self.name + "] logged in from " + self.addr[0] + " at %d:%d:%d. Last data sent at %d:%d:%d")\
        % (self.timeLogin[0],self.timeLogin[1],self.timeLogin[2],self.timeLastPost[0],self.timeLastPost[1],self.timeLastPost[2])

    # This function for the '\me' command. Allows for Role Playing style of chat
    def getMeString(self, sendString):
        return ("%d:%d:%d - " + self.name + " " + sendString) % (self.timeLastPost[0],self.timeLastPost[1],self.timeLastPost[2])

    # This function sets the timestamp of the user's most recent comment, to see if users are active
    def setLastPost(self):
        #print "Setting Post!"
        self.timeLastPost = getTime()


# This function sends the inputted string to every user that is connected
def sendToAll(sendingString):

    # This lets the Admin know what is going on
    print "Sending '" + sendingString + "' to %d users" % (len(list_of_users))

    # Here's the magical loop, go through al of the users 
    for user in list_of_users:

        # For each user, try to send the string
        try:
            user.send(sendingString)

        # This except usually happens when a user disconnects without notifying the server
        except:
            # Here, we let the admin know what happened
            print "Send failed to: " + user.name

            # It's possible that another funciton already removed the user from the list while this loop ran
            if user in list_of_users:
                # Good, the user is still in the list, let's take them out of the list...
                leaving_user = list_of_users.pop(list_of_users.index(user))
                # Close the connection with them...
                leaving_user.conn.close()
                # And tell everybody that the user is no longer in the chatroom
                sendToAll("User " + user.name + " disconnected.")

# This function simply closes all of the connections
def closeAll():
    sendToAll("Server is shutting down...")
    for user in list_of_users:
        user.conn.send("_")
        user.conn.close()


# This nasty function is a THREAD on its own.
# There is one of these threads PER user
#
# This function does the following:
# - Waits for the user to send a string.
# - If the input is a command, do the command logic.
# - ELSE, send that string to every user.
# - Disconnects the user if any errors occur.

def connectionHandler(user):

    # Get the global running variable
    global running

    # This is the threads main while
    while running:

        # There is always a posibility to have a disconnection error, that's why we have the Try
        try:

            # This line WAITS for the user to send data to the server
            inputString = user.conn.recv(4096)

            # Now that the previous line has been run, we know the user did something. Update their last interaction
            user.setLastPost()

            # Check if the string started with the \, that means it's a command
            if inputString.startswith("\\"):
                # Cut off the '\' from the string
                inputString = inputString[1:]

                # Now, if the command starts with 'help', just send the help message
                if inputString.startswith("help"):
                    user.conn.send("This chatroom is written by Steven Rogers\nJust type and send to send to all users\n" + \
                    "To change your name, type '\\setName [new name]'\n" + \
                    "To see this message again, type '\\help'\n" + \
                    "To see the list of users connected to this server, type '\\list'")

                # If the command IS 'setName'...
                elif inputString.startswith("setName"):
                    # Get the rest of the string
                    inputString = inputString[8:]

                    # Make sure it has SOME length to the string
                    if len(inputString) > 0:
                        # Set the name to what they put in
                        user.setName(inputString)
                        user.conn.send("Name changed to " + inputString)
                    else:
                        # The name isn't valid, send back that the name isn't valid
                        user.conn.send("Invalid Name")

                # If the command is 'list', the user wants a list of the other users
                elif inputString.startswith("list"):

                    # Start up a variable to holed the entire string to send
                    sendString = "Number of users connected right now: %d\n" % (len(list_of_users),)

                    # For every user, add their data to the string
                    for userData in list_of_users:
                        sendString += userData.getDataString() + "\n"

                    # Finally, send the whole string to the user who requested it
                    user.conn.send(sendString)

                # If the command is 'quit', that means the user is disconnecting from the server
                elif inputString.startswith("quit"):

                    # Be nice
                    user.conn.send("Goodbye!")

                    # Tell their chat to kill their end of the connection
                    user.conn.send("_")

                    # Take the user off of the list of connected users
                    leaving_user = list_of_users.pop(list_of_users.index(user))

                    # Close the connection on our end
                    leaving_user.conn.close()

                    # Finally, tell everybody that we disconnected this user
                    sendToAll("User " + user.name + " disconnected.")

                    # This kills the Thread
                    return None

                # The last command is the Role Playing command
                elif inputString.startswith("me ") and len(inputString) >= 4:
                    # Send the role playing version of the string to everybody
                    sendToAll(user.getMeString(inputString[3:]))

                # The command that the user sent didn't match any of our commands, so we tell the user they had a invalid command
                else:
                    user.conn.send("Invalid command")

            # So the input string isn't a command, let's treat it like it's a message
            else:

                # If it's an empty string, it's very likely the user disconnected
                if inputString == "":
                    print "User Disconnected..."
                    if user in list_of_users:
                        leaving_user = list_of_users.pop(list_of_users.index(user))
                        leaving_user.conn.close()
                        sendToAll("User " + user.name + " disconnected.")
                    pass
                else:
                    sendToAll(user.getSendString(inputString))
        except:
            if user in list_of_users:
                leaving_user = list_of_users.pop(list_of_users.index(user))
                leaving_user.conn.close()
                sendToAll("User " + user.name + " disconnected.")
            return None


# This is the Thread that allows the admin to have some control to the application
def adminOutput():

    global running

    # This is the main loop for this thread
    while running:

        # Get the raw input from the input
        sendString = raw_input()

        # If the input string starts off with a '/', it means its a command
        if sendString.startswith('\\'):

            # Get the string without the '\'
            sendString = sendString[1:]

            # Check if the admin typed in 'boot' meaning to boot a player
            if sendString.startswith("boot "):

                # Get the remaining part of the string
                sendString = sendString[5:]

                # Print out what the string is (We were having some debug issues with the above line)
                print "'" + sendString + "'"

                # Go through all the users, we need to find this one specific user
                for user in list_of_users:

                    # If the user matches the sendstring, then BOOT THEM OUT
                    if user.addr[0] == sendString:
                        user.conn.send("_")
                        user.conn.close()
                        sendToAll("Kicked user " + user.name + " ip " + user.addr[0])
                        leaving_user = list_of_users.pop(list_of_users.index(user))
                        sendToAll("User " + leaving_user.name + " disconnected.")
                        break #Breaks out of the for loop

            # If the admin typed in 'Help'
            elif sendString.startswith("help"):

                # Give the admin the help message
                print ("This chatroom is written by Steven Rogers\nJust type and send to send to all users\n" + \
                "To quit, type '\\quit'\n" + \
                "To see this message again, type '\\help'\n" + \
                "To see the list of users connected to this server, type '\\list'")

            # If the admin typed in list..
            elif sendString.startswith("list"):

                # Print the amount of users who are connected
                print "%d users connected" % (len(list_of_users))

                # Loop through the list and print out their data
                for user in list_of_users:
                    print user.getDataString()

            # If the admin typed in 'quit'
            elif sendString.startswith("quit"):

                # Grab the running variable
                global running
                # Set running to false
                running = False

                # Set the server to closing down
                print "Closing down the server...."

                ##
                ####  When running is false, it will trigger the "closeAll()" function
                ####  That will take care of all of the connections
                ##

                # This will end the thread
                return

            # The command didn't match any of our possible commands
            else:
                # Let the admin know iw wasn't a posible command
                print "Invalid Command\n Type '\\help' to see the list of possible commands"

        # The string didn't start with a '\' so we know it's not a command.
        else:
            # Send the message to all the users normally
            sendToAll("[admin] > " + sendString)


# This thread waits for new connections and adds them to the list of users
def waitForConnections(s):

    global running

    # This is the main loop for this thread
    while running:

        # Let the admin know that we are waiting for a new connection
        print "Waiting for connection..."

        # This establishes a connection with a client. It doesn't pass this line till a connection is created.
        c, addr = s.accept()    

        # Let the admin know we got a conneciton
        print 'Got connection from', addr

        # Get the name that the user set when they connected
        tmpName = c.recv(1024)

        # Send the message to the user for successfully connecting
        c.send('Thank you for successfully connecting!\n')

        # Create the temporary user
        tmpUser = User(c,addr,tmpName)

        # Start the thread that wll listen to that user and give it the user
        thread.start_new_thread(connectionHandler,(tmpUser,))

        # Add that new user to the list of connected users
        list_of_users.append(tmpUser)

        # Let everybody know that our new user joined the party
        sendToAll("New user " + tmpName + " connected from " + addr[0])


# Start the admin's thread first
thread.start_new_thread(adminOutput,())

# Create a new socket for all of the connections
s = socket.socket()

# Print the ip address we are running on
print([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1])


# Try to get the local host name
host = socket.getfqdn()

# These are for debugging:
print "socket.gethostname(): " + socket.gethostname()
print "socket.getfqdn(): " + socket.getfqdn()

# This lets the admin know which IP we are going to broadcast on
print "\nYour server is hosting on local IP address:"
print socket.gethostbyname(host)
print host

# The final message suggests the '\help' command for the Admin
print "Type '\\help' for a list of admin commands"

# The hard-coded port number (Same as the client's)
port = 9002

# Bind our socket to the 'host' (socket.getfqdn()) and the 'port' (9002)
s.bind((host, port))

# This prints out the socket name
print "s.getsockname(): " + s.getsockname()

# Listen (total buffered listeners 5)
s.listen(5)

# Start up the thread that waits for connections
thread.start_new_thread(waitForConnections,(s,))


# While the server is up and running, just loop here and let the threads do all the work
while running:
    pass

# The server has crashed or closed somewhere causing 'running' to change to False
# So close all of teh connections
closeAll()

# Close the socket
s.close()

# Give a goodnight message
print "\nGoodnight"