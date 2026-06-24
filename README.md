# Basic File-Sharing System
**Network & Distributed Programming — Group 4 Project**

---

## Overview
A client-server file-sharing application built with Python's built-in `socket`
and `threading` modules. No third-party packages are required. This system demonstrates
fundamental network programming concepts including socket communication, concurrent
connections, and file transfer protocols.

---

## Architecture

### System Design
```
CLIENT                          SERVER
  │                               │
  │── UPLOAD filename size ──────►│
  │── <file bytes> ──────────────►│  saves to server_storage/
  │◄─ OK / ERROR ─────────────────│
  │                               │
  │── DOWNLOAD filename ─────────►│
  │◄─ OK <filesize> ──────────────│
  │◄─ <file bytes> ───────────────│
  │                               │
  │── LIST ──────────────────────►│
  │◄─ OK\n file1\n file2\n END ───│
  │                               │
  │── EXIT ──────────────────────►│
  │◄─ OK: Goodbye. ───────────────│
```

### Network Protocol
The system uses a custom text-based protocol over TCP sockets:
- **Command Format**: `COMMAND <filename> <size>` (for upload)
- **Response Format**: `STATUS: <message>` or `OK: <details>`
- **File Transfer**: Binary data sent after command acknowledgment
- **Connection**: Persistent connection maintained until EXIT command

### Threading Model
- Server uses threading to handle multiple concurrent clients
- Each client connection spawns a new thread
- Thread-safe file operations using locks

---

## Project Structure
```
file_sharing/
├── server.py          ← Run this on the machine acting as the server
├── client.py          ← Run this on any machine that wants to share files
├── README.md          ← This file
└── docs/
    └── protocol.md    ← Detailed protocol specification
```

**Runtime Directories** (created automatically):
- `server_storage/` - Files stored on the server
- `client_downloads/` - Files downloaded by clients

---

## Installation

### Prerequisites
- Python 3.7 or higher installed on your system
- No additional packages required (uses only standard library)

### Setup Steps
1. **Clone or download** the project files to your local machine
2. **Verify Python installation**:
   ```bash
   python --version
   # Should show Python 3.7+
   ```
3. **No installation needed** - the system uses only Python standard library

---

## How to Run

### 1. Start the Server
```bash
python server.py
```
The server listens on port **5001** by default.

**Server Output:**
```
[SERVER] Starting file-sharing server on 0.0.0.0:5001
[SERVER] Storage directory: server_storage/
[SERVER] Waiting for connections...
```

### 2. Start a Client (same machine or different machine)
```bash
python client.py
```
If the client is on a different machine, edit `SERVER_HOST` in `client.py`
to point to the server's IP address before running.

**Client Output:**
```
[CLIENT] Connected to server at 127.0.0.1:5001
>>> 
```

### 3. Using the System
Once connected, use the interactive prompt:
```
>>> upload /path/to/file.txt
>>> list
>>> download file.txt
>>> exit
```

---

## Configuration

### Server Configuration (server.py)
- `HOST = "0.0.0.0"` - Listen on all interfaces
- `PORT = 5001` - Server port
- `STORAGE_DIR = "server_storage/"` - Where files are stored
- `MAX_CLIENTS = 5` - Maximum concurrent connections

### Client Configuration (client.py)
- `SERVER_HOST = "127.0.0.1"` - Server IP address (change for remote server)
- `SERVER_PORT = 5001` - Server port
- `DOWNLOAD_DIR = "client_downloads/"` - Where downloaded files are saved

---

## Network Setup (Different Machines)

### To run client on a different laptop:

**Step 1: Find your server's IP address**
- **Windows**: Open Command Prompt and run `ipconfig`
  - Look for "IPv4 Address" under your network adapter
- **Mac/Linux**: Run `ifconfig` or `ip addr`

**Step 2: Edit client.py on the other laptop**
```python
SERVER_HOST = "YOUR_SERVER_IP"  # e.g., "192.168.1.100"
```

**Step 3: Network requirements**
- Both laptops must be on the **same network** (WiFi or LAN)
- **Windows Firewall**: Allow port 5001 or run as administrator
- **Router**: No port forwarding needed for same network

**Step 4: Run the system**
- **Your laptop**: `python server.py`
- **Other laptop**: `python client.py`

---

## Available Commands (from the client prompt)

| Command | Description |
|---------|-------------|
| `upload <path>` | Upload a local file to the server |
| `download <name>` | Download a file stored on the server |
| `list` | List all files currently stored on the server |
| `help` | Show the command reference |
| `exit` | Disconnect from the server |

### Example Session
```
>>> upload report.pdf
[SERVER] OK: 'report.pdf' uploaded successfully (45312 bytes).

>>> list
[SERVER] Files available:
  • report.pdf

>>> download report.pdf
[CLIENT] Download complete: 'client_downloads/report.pdf' (45312 bytes)

>>> exit
[SERVER] OK: Goodbye.
```

---

## Technical Implementation

### Server Components
- **Socket Listener**: Accepts incoming client connections
- **Client Handler**: Processes commands from each client
- **File Manager**: Handles file storage and retrieval
- **Thread Manager**: Manages concurrent client connections

### Client Components
- **Command Parser**: Interprets user input
- **Socket Connector**: Maintains connection to server
- **File Transfer Handler**: Manages upload/download operations
- **Response Handler**: Processes server responses

### Data Flow
1. Client connects to server via TCP socket
2. Client sends command (UPLOAD, DOWNLOAD, LIST, EXIT)
3. Server processes command and responds
4. For file transfers, binary data is sent after acknowledgment
5. Connection remains open until EXIT command

### Message Protocol Details
- **Buffer Size**: 4096 bytes for command messages
- **Chunk Size**: 1024 bytes for file data transfer
- **Encoding**: UTF-8 for text, binary for file data
- **Message Delimiter**: Newline character (`\n`)

### Error Handling
- Connection timeout handling
- File not found errors
- Invalid command responses
- File size validation
- Network interruption recovery

---

## Requirements
- Python 3.7 or higher
- No external libraries needed

---

## Network Concepts Demonstrated
- TCP socket programming
- Client-server architecture
- Concurrent connection handling with threads
- Binary file transfer over sockets
- Custom protocol design
- Error handling in network applications
- Socket buffer management
- Thread synchronization with locks

---

## Implementation Notes

### Server Implementation
```python
# Key server components to implement:
# 1. Socket setup and binding
# 2. Accept client connections in a loop
# 3. Spawn thread for each client
# 4. Parse commands and handle file operations
# 5. Send appropriate responses
```

### Client Implementation
```python
# Key client components to implement:
# 1. Connect to server socket
# 2. Read user input and parse commands
# 3. Send commands to server
# 4. Handle file upload/download with progress
# 5. Display server responses
```

---

## Testing Strategy
- Test single client upload/download
- Test multiple concurrent clients
- Test large file transfers
- Test error conditions (file not found, invalid commands)
- Test network interruption scenarios

---

## Future Enhancements
- Add user authentication
- Implement file permissions
- Add resume capability for large files
- Implement file compression
- Add encryption for secure transfers