BEROCHAT - NETWORKING PROTOCOL DOCUMENTATION
==============================================

## SENDING PROTOCOL

Messages are sent in 3 parts:
1. **Length Header** (128 bytes): Size of the info section
2. **Info String** (variable): Contains message length, type, and extra info
3. **Actual Message** (variable): The pickled message content

Format: `[msg_len]/[msg_type]/[xinfo]`

---

## MESSAGE TYPES

### Sent BY CLIENT to SERVER:

| Type | Name | Description | xinfo |
|------|------|-------------|-------|
| `pums` | Public Message | Message visible to all users | (empty) |
| `prms` | Private Message | Message to specific user | receiver username |
| `naif` | Name Info | Initial username registration | (empty) |
| `dscn` | Disconnect | Client disconnecting | (empty) |

### Sent BY SERVER to CLIENT:

| Type | Name | Description | xinfo |
|------|------|-------------|-------|
| `pums` | Public Message | Message from another user | sender username |
| `prms` | Private Message | Private message from user | sender username |
| `prcf` | Private Confirmation | Confirms private message sent | receiver username |
| `clif` | Client Info | List of connected clients | (empty) |
| `eror` | Error | Server error message | (empty) |
| `mdct` | Message Dict | Message history for user | (empty) |

---

## MESSAGE EXAMPLES

### Example 1: Public Message
```
Client sends: "Hello everyone!"
Type: pums
Server broadcasts to all with sender name
```

### Example 2: Private Message
```
Client sends: "Hello Alice" 
Type: prms with xinfo="Alice"
Server routes to Alice only and sends confirmation back
```

### Example 3: Registration
```
Client connects and sends username "Bob"
Type: naif
Server adds to client list and broadcasts updated client list
```

---

## MESSAGE STORAGE

### Server-Side Storage:

**msg_dict** - Dictionary storing all messages:
```python
{
    "public": [["message1", "user1"], ["message2", "user2"], ...],
    "user1/user2": [["private msg", "user1"], ...],
    "user2/user3": [["private msg", "user2"], ...]
}
```

- Public messages all stored under "public" key
- Private messages stored under alphabetically sorted key: "user1/user2"
- When client connects, they receive only relevant messages

**msg_list** - Simple list of all public messages (deprecated)

**client_list** - Array of connected clients:
```python
[[connection, address, username], ...]
```

---

## CONNECTION FLOW

1. **Client connects to server** (TCP socket)
2. **Client sends name** (type: naif)
3. **Server registers client** and broadcasts updated client list
4. **Client receives message history** (type: mdct)
5. **Client/Server exchange messages** (pums, prms, etc.)
6. **Client disconnects** (type: dscn)
7. **Server removes client** and broadcasts updated list

---