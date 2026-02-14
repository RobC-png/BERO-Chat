"""CLI chat client with public and private messaging support."""

import socket
import pickle
import threading

# Server connection settings
IP = "127.0.0.1"
PORT = 5050
FORMAT = "utf-8"
HEADER = 128
SEPERATION_STR = "/"

def send_message(client, msg, msg_type, xinfo=""):
    """Send a message to the server using the protocol"""
    message = pickle.dumps(msg)
    message_len = str(len(message))
    
    info_str = message_len + SEPERATION_STR + msg_type + SEPERATION_STR + xinfo
    info = info_str.encode(FORMAT)
    info_len = str(len(info))
    
    length = info_len.encode(FORMAT)
    length += b' ' * (HEADER - len(length))
    
    client.send(length)
    client.send(info)
    client.send(message)

def receive_message(client):
    """Receive a message from the server using the protocol"""
    length = client.recv(HEADER).decode(FORMAT)
    
    if length:
        info_length = int(length)
        info_str = client.recv(info_length).decode(FORMAT)
        
        info_list = info_str.split(SEPERATION_STR)
        msg_len = int(info_list[0])
        msg_type = info_list[1]
        xtra_info = info_list[2]
        
        msg = pickle.loads(client.recv(msg_len))
        
        return msg, msg_type, xtra_info
    
    return None, None, None

def receive_thread(client, username):
    """Thread function to continuously receive messages from the server"""
    while True:
        try:
            msg, msg_type, xtra_info = receive_message(client)
            
            if msg is None:
                break
            
            # Don't display own messages
            if xtra_info == username and msg_type in ["pums", "prms"]:
                continue
            
            if msg_type == "pums":
                print(f"\n[PUBLIC] {xtra_info}: {msg}")
            elif msg_type == "prms":
                print(f"\n[PRIVATE] {xtra_info}: {msg}")
            elif msg_type == "clif":
                print(f"\n[CLIENTS ONLINE] {msg}")
            elif msg_type == "eror":
                print(f"\n[ERROR] {msg}")
                
            # Reprint the input prompt
            print("", end="", flush=True)
        except:
            break

def main():
    """Main function for CLI chat client."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((IP, PORT))
        print(f"Connected to server at {IP}:{PORT}")
    except ConnectionRefusedError:
        print("Error: Could not connect to server")
        return
    
    # Get username
    username = input("Enter your username: ")
    send_message(client, username, "naif")
    
    print(f"Connected as: {username}")
    print("Commands: type message, 'quit' to exit, '@username message' for private message")
    print("-" * 50)
    
    # Start receive thread
    recv_thread = threading.Thread(target=receive_thread, args=(client, username), daemon=True)
    recv_thread.start()
    
    while True:
        try:
            # Send message
            msg_input = input(f"{username}: ")
            
            if msg_input.lower() == 'quit':
                send_message(client, "", "dscn")
                break
            
            # Check if it's a private message
            if msg_input.startswith('@'):
                parts = msg_input.split(' ', 1)
                if len(parts) >= 2:
                    receiver = parts[0][1:]  # Remove @ symbol
                    message = parts[1]
                    send_message(client, message, "prms", receiver)
            else:
                # Public message
                send_message(client, msg_input, "pums")
            
        except KeyboardInterrupt:
            send_message(client, "", "dscn")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    client.close()
    print("Disconnected from server")

if __name__ == "__main__":
    main()
