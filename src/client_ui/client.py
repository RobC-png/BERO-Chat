"""GUI-based chat client using CustomTkinter for modern UI."""

import pickle
import socket
import os
import threading
import customtkinter
import tkinter
from tkinter import *
from customtkinter import *
from PIL import Image

# Message type codes
# Sent by client: pums (public message), prms (private message), naif (name info), dscn (disconnect)
# Sent by server: pums (public message), prms (private message), mdct (message dictionary),
#                 eror (error), clif (client info), prcf (private message confirmation)

# Server connection settings
HEADER = 128
PORT = 5050
FORMAT = 'utf-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

# UI Configuration
FONT = "Consolas"
SEPERATION_STR = "/"
LIGHT_BG_GREY = "#343638"
DARK_BG_GREY = "#2a2d2e"
LIME_GREEN = "#11b384"
MAX_CONNECTED_CLIENTS = 30



# Application state
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
username = ""
client_list = []
pr_msg_receiver = 0  # 0 for group chat, ID for private message recipient
msg_dict = {}

# UI state
chat_frame_height = 100
chat_entry_count = 0
connected_clients_count = 0
client_buttons_list = []
current_labels = []





def connect():
    """Establish connection to the server and start receive thread."""
    global connected
    try:
        client.connect(ADDR)
        connected = True
        changeServerButtonToDisconnect()
        rec_thread = threading.Thread(target=receive, daemon=True)
        rec_thread.start()
    except ConnectionRefusedError:
        print("[ERROR] Could not connect to server")
    
    send(username, "naif")
    

def startConnectingThread():
    connectThread = threading.Thread(target=connect)
    connectThread.start()

def LoginButton():
    """Handle login button click - save username and transition to main chat interface."""
    global username_area, username, username_label, client_list
    
    username = username_area.get()
    if username:
        client_list = ["Group Chat", username]
        handleClienList(client_list)
        username_label.configure(text=username)
        load_frame(frame_main)
    else:
        print("Please enter a username")


def changeServerButtonToDisconnect():
    """Update server button text when connected."""
    global server_button
    server_button.configure(text="Disconnect From Server")


# Networking functions
def send(msg, msg_type, *xinfo):
    """Send a message to the server using the protocol."""
    message = pickle.dumps(msg)
    message_len = str(len(message))
    
    info_str = message_len + SEPERATION_STR + msg_type + SEPERATION_STR + str(*xinfo)
    info = info_str.encode(FORMAT)
    info_len = str(len(info))
    
    length = info_len.encode(FORMAT)
    length += b' ' * (HEADER - len(length))
    
    client.send(length)
    client.send(info)
    client.send(message)


#converts a percentage to pixels
def rel_Width(_1440p_number):   #if this does not work just input a percentage
    global window
    width = window.winfo_screenwidth()    

    factor = _1440p_number / 2560
    correct_value = factor * width
    return correct_value
    
def rel_Height(_1440p_number):
    global window
    heigth = window.winfo_screenheight()

    factor = _1440p_number / 1440
    correct_value = factor * heigth
    return correct_value

def receive():
    
    global connected
    
    #receiving 3 msg: length, info, message
    
    while connected:
        
        length = client.recv(HEADER).decode(FORMAT)
        
        if length:
            
            info_length = int(length)
            info_str = client.recv(info_length).decode(FORMAT)
            
            info_list = info_str.split(SEPERATION_STR) #test/haha/test.split("/") ==> ["test","haha","test"]
            msg_len = int(info_list[0])
            msg_type = info_list[1]
            xtra_info = info_list[2]
            
            pclmsg = client.recv(msg_len)
            msg = pickle.loads(pclmsg)
            
            handle_msg(msg, msg_type, xtra_info)
    
def handle_msg(msg, type, *xinfo):
    
    #pums = public message
    #prms = private message
    #eror = ERROR
    #clif = client info
    global msg_dict
    
    if type == "pums":
        
        sender = str(*xinfo)
        print_str = sender + ": " + msg
        saveMsgToDict(msg, type, sender)
        print_msg(print_str)
        
    elif type == "prms":
        
        sender = str(*xinfo)
        print_str = sender + ": " + msg
        saveMsgToDict(msg, type, sender, [username, sender])
        print_msg(print_str)
    
    elif type == "prcf":
        
        recv = str(*xinfo)
        print_str = username + ": " + msg
        print_msg(print_str)
        
        saveMsgToDict(msg, type, username, [username, recv])
    
    elif type == "eror":
        
        #maybe color it red?
        print_msg(msg)
        
    elif type == "clif":
        
        msg = "Group Chat" + SEPERATION_STR + msg #make group chat the first item in the list
        new_client_list = msg.split(SEPERATION_STR)
        handleClienList(new_client_list)
        
    elif type == "mdct":
        
        print("[Current MSG]:", msg)
    
    
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
    

#function which gets called from the send button
def send_button_(): 
    global input_area

    recv = ""
    msg = input_area.get() #creates a new variable [msg] based on what is in the entry box
        
    if not pr_msg_receiver == 0:
            
        recv = client_list[pr_msg_receiver]
        type = "prms"
        
    else:
            
        type = "pums"
    
    send(msg, type, recv) #send the message
        
    input_area.delete(0, END) #clear the entry box

        
#print the message onto the tkinter window
def print_msg(msg):
    #insert new text to the entry box
    global frame_labels
    global canvas
    global resize_frame
    global chat_frame_height
    global chat_entry_count
    global frame_canvas
  

    new_label = customtkinter.CTkLabel(master=frame_labels,
                                                text=msg,
                                                font=(FONT, 15),
                                                height=40,
                                                corner_radius=7,
                                                fg_color=(DARK_BG_GREY),
                                                anchor="w")


    new_label.pack(side=TOP, anchor=NW, padx=10, pady=5)
    current_labels.append(new_label)

    #figure out the new height
    chat_entry_count += 1
    if frame_canvas.winfo_height() < chat_entry_count*MSG_HEIGHT:
        chat_frame_height = chat_entry_count*MSG_HEIGHT + 8
    else:
        chat_frame_height = frame_canvas.winfo_height()


    canvas.itemconfig(resize_frame, height=chat_frame_height)
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto( 1 )


#for exiting the window properly (if the x is clicked)
def stopWindow():
    global window
    print('stop')
    try:
        send("", "dscn")
    except Exception:
        pass
    window.destroy()
    exit(0)

def toggleFullscreen():
    global window
    if (window.attributes('-fullscreen')):
        window.attributes('-fullscreen', False)
    else:
        window.attributes('-fullscreen', True)

#changes the Ui based on the new list of connected clients
def handleClienList(new_client_list):
    global client_buttons_list
    global client_list
    global connected_clients_count

    #delete the old UI
    for i in range (len(client_buttons_list)):
        client_buttons_list[i].destroy()

    #clear the list
    client_buttons_list.clear()

    #update to the new list
    client_list = new_client_list
    connected_clients_count = len(new_client_list)
    

    #call the instantiating of the new UI
    refreshUIofExistingClients()


#if a new client connects, but there are already others connected
def refreshUIofExistingClients():   
    for i in range (connected_clients_count): 
        newClientConnectedUI(i, i + 1) 


#to handle the contacts list correctly
def newClientConnectedUI(user_id, row):
    global frame_main
    unavaiable_rows = 5
    _row = unavaiable_rows + row
    username = client_list[user_id]

    #add a new Label 
    newButton = CTkButton(frame_main, text=username, font=(FONT, 12), command=lambda: ContactButtonEvent(user_id), height=rel_Height(45), border_width=3, border_color=LIME_GREEN, fg_color=DARK_BG_GREY) 
    newButton.grid(row=_row, column=0, sticky="nesw",padx=rel_Width(20) ,pady=rel_Height(8))    
    client_buttons_list.append(newButton)



#just in case we need this later (for future proofing, not in use currently)
def clientDisConnectedUI(clientIndex, newClientCount):
    #remove label and checkbox from the screen
    client_buttons_list[clientIndex].destroy()

    #remove label and checkbox from the lists
    client_buttons_list.pop(clientIndex)
 


#light and dark mode
def change_appearance_mode(new_appearance_mode):
    if(new_appearance_mode=="Pink"):
        global frame_main
        frame_main.configure(bg="pink")
    else:
        customtkinter.set_appearance_mode(new_appearance_mode)


#for switching between frames
def load_frame(frame):
    frame.tkraise()





#checkboxes events
def ContactButtonEvent(id):
    global only_one_pr_msg
    global pr_msg_receiver
    global username
    global client_list

    pr_msg_receiver = id

    #switcht the color on on the right button
    for i in range (len(client_buttons_list)):
        client_buttons_list[i].configure(fg_color=DARK_BG_GREY)

    client_buttons_list[id].configure(fg_color=LIME_GREEN)

    if id == 0:
        #group chat
        str_ = "public"
    else:
        str_ = str(username) + SEPERATION_STR + str(client_list[pr_msg_receiver])

    if not str_ in msg_dict:
        msg_dict[str_] = []
                
    switchChat(msg_dict[str_])




#function to recreate the chat when the receipient is swithed
def switchChat(chat_history):
    global current_labels
    global chat_entry_count
    print(chat_history, "DEBUG")

    chat_entry_count = 0

    #delete all the labels from the chat
    for i in range (len(current_labels)):
        current_labels[i].destroy()

    #cler the list
    current_labels.clear() 


    for i in range(len(chat_history)):
        msg = chat_history[i][0]
        sender = chat_history[i][1]

        print_str = sender + ": " + msg
        print_msg(print_str)



def init_UI():
    global input_area
    global window
    global server_button
    global frame_main
    global frame_login
    global frame_labels
    global canvas
    global username_area
    global username_label
    global resize_frame
    global frame_canvas
    global MSG_HEIGHT

    file_path = None
    script_dir = os.path.dirname(os.path.abspath(__file__))

    #window, name, logo
    window = CTk()
    window.title("BERO Chat")
    window.state('zoomed')
    MSG_HEIGHT = 50

    # Try to load icon
    try:
        ico_path = os.path.join(script_dir, "logo.ico")
        if os.path.exists(ico_path):
            window.iconbitmap(ico_path)
    except Exception:
        pass

    #create the frames
    frame_main = CTkFrame(window)
    frame_login = CTkFrame(window)
    for frame in (frame_main, frame_login):
        frame.grid(row=0,column=0,sticky='nsew')

    customtkinter.set_default_color_theme("green")

    #create the grid system:
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    frame_main.grid_rowconfigure(28, weight=1)
    frame_main.grid_columnconfigure(2, weight=1)
    frame_login.grid_rowconfigure((4), weight=1)
    frame_login.grid_columnconfigure(2, weight=1)


    chat_label = CTkLabel(frame_main, text="Settings/Chat")
    chat_label.configure(font=(FONT, 15))
    chat_label.grid(row=0, column=0, padx=(20, 80))

    _Checkbox = customtkinter.CTkCheckBox(master=frame_main, text="", command=toggleFullscreen)
    _Checkbox.grid(row=0, column=1, sticky="nw", pady=30)

    chat_label = CTkLabel(frame_main, text="Chat:", text_color="white")
    chat_label.configure(font=(FONT, 15))
    chat_label.grid(row=0, column=2)


    #connect to server button
    server_button = CTkButton(frame_main, text="Connect to Server", command=startConnectingThread, corner_radius=5, font=(FONT, 15), width=80, height=50)
    server_button.grid(row=1, column=0, sticky="ne", pady=30)

    info_label = CTkLabel(frame_main, text="Logged in as:", text_color="white", font=(FONT, 15))
    info_label.grid(row=2, column=0)

    username_label = CTkLabel(frame_main, text="[USERNAME]", text_color="white", font=(FONT, 15))
    username_label.grid(row=3, column=0, pady=(0, 20))

    #message entry box
    input_area = CTkEntry(frame_main, border_width=0, font=(FONT, 13))
    input_area.grid(row=40, column=2, sticky="nsew", pady=10)

    #send button
    send_button = CTkButton(frame_main, text="send", command=send_button_, corner_radius=5, font=(FONT, 12), width=rel_Width(80), height=rel_Height(50))
    send_button.grid(row=40, column=3, columnspan=2, pady=10, padx=(0, 10))

   
    #light and dark mode
    optionmenu_1 = customtkinter.CTkOptionMenu(master=frame_main, values=["Dark", "Light", "System", "Pink"], command=change_appearance_mode)
    optionmenu_1.grid(row=40, column=0, pady=10, padx=20, sticky="nesw")

    #Create a frame for the canvas with non-zero row&column weights
    frame_canvas = CTkFrame(frame_main, border_width=0)
    frame_canvas.grid(row=1, column=2, columnspan=2, rowspan=35, sticky="nesw")
    frame_canvas.grid_rowconfigure(0, weight=1)
    frame_canvas.grid_columnconfigure(0, weight=1)
    frame_canvas.grid_propagate(False)

    # Add a canvas in that frame
    canvas = tkinter.Canvas(frame_canvas, highlightthickness=0, bg=DARK_BG_GREY)
    canvas.grid(row=0, column=0, sticky="news", columnspan=30)

    # Link a scrollbar to the canvas
    vsb = CTkScrollbar(frame_main, command=canvas.yview)
    vsb.grid(row=1, column=4, rowspan=35, sticky="ns", padx=(0, 10))
    canvas.configure(yscrollcommand=vsb.set)

    # Create a frame to contain the buttons
    frame_labels = CTkFrame(canvas, fg_color=LIGHT_BG_GREY)
    resize_frame = canvas.create_window((0, 0), window=frame_labels, anchor='nw',width=frame_canvas.winfo_width(), height=frame_canvas.winfo_height())

    # Update buttons frames idle tasks to let tkinter calculate buttons sizes
    frame_labels.update_idletasks()

    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas.bbox("all"))

    #===LOGIN FRAME===========================================================================
    chat_label = CTkLabel(frame_login, text="Enter your username", text_color="white", anchor= CENTER)
    chat_label.configure(font=(FONT, 20))
    chat_label.grid(row=1, column=2, pady=20, sticky="n",)

    # #message entry box
    username_area = CTkEntry(frame_login, border_width=0, height=rel_Height(70), width=rel_Width(300), font=(FONT, 12))
    username_area.grid(row=2, column=2, sticky="n", pady=20)

    #login button
    send_button = CTkButton(frame_login, text="Login", command=LoginButton, corner_radius=5, font=(FONT, 20), width=rel_Width(160), height=rel_Height(80))
    send_button.grid(row=3, column=2, sticky="n", pady=(50, 20))

    #for exiting the window properly
    window.protocol("WM_DELETE_WINDOW", stopWindow)

    refreshUIofExistingClients()
    load_frame(frame_login)

    window.mainloop()


init_UI()
