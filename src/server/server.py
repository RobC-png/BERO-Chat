# import libraries
from enum import Flag
import socket #for networking
import threading #for running multiple things at once
import pickle

#MSG types
#pums = public message
#clif = client info
#prms = private message
#eror = ERROR
#naif = name info

#recv by server
#pums = public message
#prms = private message
#naif = name info
#dscn = disconnect

#sent by server
#pums = public message
#prms = private message
#eror = ERROR
#clif = client info

#set standard valuessa
HEADER = 128 #byte-ammount to transmit the length of the message
PORT = 5050 #port (door) the server is using
SERVER = "127.0.0.1" #gets the IP adress of the server | Robin PC: "192.168.0.45" | Benni PC: "192.168.0.80"
ADDR = (SERVER, PORT) #combines [SERVER] and [PORT] into [ADDR] tupel 
FORMAT = 'utf-8' #sets the standard text encoding
DISCONECT_MSG = "!DISCONNECT" #message to disconnect from the server
SEPERATION_STR = "/"

#lists
msg_dict = {}
msg_list = [] #create an empty list
client_list = [] #[[conn, addr, name], [conn, addr, name]]


#setting up the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates a server object and sets parameters (type of data, type of sending it)
server.bind(ADDR) #binds the server to the IP and port of [ADDR]


#starting the server
def start():
    server.listen() #listens for connections of clients that want to connect and waits until one is found
    print(f"[LISTENING ON] {SERVER}")
    while True: #constantly handles new clients
        conn, addr = server.accept() #accepts the connection to a client and saves their [conn](road) and addr
        thread = threading.Thread(target=handle_client, args=(conn, addr)) #creates a new thread for the new client and passes the clients information to the thread
        thread.start() #starts the thread
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def sendCLientInfo():
    
    currentClients = ""
    
    global client_list
    for i in range(len(client_list)):
        
        if not i == len(client_list) - 1:
            currentClients += client_list[i][2] + "/"
        else:
            currentClients += client_list[i][2]
        
    send_to_all(currentClients, "clif")

def AddClientToList(conn, addr, name):
    
    #adds all the client info to the [client_list]
    client_list.append([conn, addr, name])
    sendCLientInfo()
    
    
def SubClientFrList(nr):
    
    #removes the client form [client_list]
    client_list.pop(nr)
    sendCLientInfo()
    
def sendMSGdict(user, conn):
    
    public_msgs = False
    send_dict = {} #set up emtpy dict to send
    if "public" in msg_dict: #only adds stuff if the key allready exists
        
        send_dict["public"] = msg_dict["public"] #add the public chat to the send_dict
        public_msgs = True
    
    
    if len(msg_dict) == 1 and public_msgs == False or len(msg_dict) > 1:  #if there are prvate msgs
        
        for key in msg_dict: #for every key in the msg_dict
            
            if not key == "public": #if it is any other convo than the private one 
                
                people = key.split(SEPERATION_STR) #gets all participants of the convo based on the key ("USER1/USER2")
                for person in people: #for every participant
                    
                    if user == person: #if the participant is the user you want to send the dict to
                        
                        send_dict[key] = msg_dict[key] #add that convo to the send_dict
                    
    send(send_dict, conn, "mdct") #sends the send_dict to the user
        
        
    

#thread for the client, every client gets their own loop
def handle_client(conn, addr): #takes in [conn] and [addr] to know which client to handle
    
    global client_list
    
    #sets up some variables for handeling the client
    name = ""
    connected = True
    print(f"[CONECTED TO] {addr}")    
    
    
    while connected: #constantly waits to receive new messages
        
        msg, type, xinfo = receive(conn) #waits to receive a new message
        
        if type == "naif":
            
            name = msg #saves the name of the client
            AddClientToList(conn, addr, name)
            sendMSGdict(name, conn) #after the client registers themself with a name, they get all messages impotanat to them
        
        elif type == "pums":
            
            print(f"[MESSAGE FROM: {addr} | {name}] {msg}")
            send_to_all(msg, "pums", name)
            
            saveMsgToDict(msg, type, name)
            
            saveMsgToList(msg)
        
        elif type == "prms":
                
            found_recv = False
            search_done = False
            recv = xinfo
            i = 0
            
            while found_recv == False and search_done == False: #goes through all connected clients
                
                if client_list[i][2] == recv: #if a name on [clients_list] matches with the receiver
                        
                    if not name == recv: #if it is a chat between 2 people
                    
                        send(msg, client_list[i][0], "prms", name) #send [msg] to that client
                        send(msg, conn, "prcf", recv) #send confirmation to the sender
                        
                    else: #if it is 1 person msging themselves then only send 1 msg
                        
                        send(msg, client_list[i][0], "prms", name)
                    
                    saveMsgToDict(msg, type, name, [name, recv])
                    
                    found_recv = True
                
                i += 1 #increases the number of search trys
                
                if i == len(client_list): #if it has tried for every client
                    
                    search_done = True #the loop stops
            
            if found_recv == False:
                
                msg = "[SERVER MSG]: Recipiant couldn't be found, \n please check if the input was correct"
                send(msg, conn, "eror")
                
        
        elif type == "dscn":
            
            for i in range(len(client_list)): #goes through the [client_list]
                
                if client_list[i][1] == addr: #if it finds the current client
                    
                    SubClientFrList(i)
                    print(f"[DISCONECTED FROM] {addr}")
                    connected = False
        
        

    conn.close() #closes the connection to the client



#function for receiving and encoding messages
def receive(conn): #takes in [conn] to know from whom to receive the message
    
    length = conn.recv(HEADER).decode(FORMAT)
        
    if length:
        
        info_length = int(length)
        info_str = conn.recv(info_length).decode(FORMAT)
        
        info_list = info_str.split(SEPERATION_STR)
        msg_len = int(info_list[0])
        msg_type = info_list[1]
        xtra_info = info_list[2]
        
        msg = pickle.loads(conn.recv(msg_len))
        
        return msg, msg_type, xtra_info



#function for sending messages
def send(msg, conn, type, *xinfo): #takes in [msg] and [conn] to know to which client to send the message
    
    #sending 3 msg: length, info, message
    
    message = pickle.dumps(msg) #encodes the message in binary
    message_len = str(len(message))
    
    info_str = message_len + SEPERATION_STR + type + SEPERATION_STR + str(*xinfo)
    info = info_str.encode(FORMAT)
    info_len = str(len(info))
    
    length = info_len.encode(FORMAT)
    length += b' ' * (HEADER - len(length))
    
    conn.send(length)
    conn.send(info)
    conn.send(message)


#function for sending one message to every connected client
def send_to_all(msg, type, *xinfo):
    global client_list #use the global [client_list]
    for i in range(len(client_list)): #for every client there is
        conn = client_list[i][0] #gets the correct connection to the client
        send(msg, conn, type, *xinfo)


#save every message to a list
def saveMsgToList(new_msg):
    msg_list.append(new_msg) #adds the new message to [msg_list]
    print("[NEW MESSAGE! CURRENT LIST: ", msg_list)
    
def saveMsgToDict(msg, type, sender, *userlist):
    
    data = [msg, sender]
    
    if type == "pums":
        
        key = "public"
        
        if key in msg_dict:
            
            msg_dict["public"].append(data)
            
        else:
            
            msg_dict[key] = [data]
        
    if type == "prms":
        
        userlist = list(userlist[0])
        userlist.sort(key=str.lower)
        print(userlist)
        
        user1 = userlist[0]
        user2 = userlist[1]
        key = user1 + SEPERATION_STR + user2
        
        if key in msg_dict:
            
            msg_dict[key].append(data)
            
        else:
            
            msg_dict[key] = [data]
        
    print(msg_dict)
        
        



print("[SERVER STARTING]")
start()
