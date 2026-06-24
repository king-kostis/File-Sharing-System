# Protocol Specification
**File-Sharing System - Network Protocol**

---

## Overview
This document specifies the custom text-based protocol used for communication
between the client and server in the file-sharing system.

---

## Connection Setup

### Server Configuration
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `5001` (default)
- **Protocol**: TCP
- **Encoding**: UTF-8

### Client Connection
- **Server Host**: `127.0.0.1` (localhost, configurable)
- **Server Port**: `5001` (default)
- **Connection Timeout**: 10 seconds

---

## Message Format

### General Format
```
<COMMAND> [arguments] <newline>
```

All commands are terminated with a newline character (`\n`).

### Response Format
```
<STATUS> <message> <newline>
```

Responses are also terminated with a newline character.

---

## Commands

### 1. UPLOAD Command

**Client to Server:**
```
UPLOAD <filename> <filesize>
```

**Example:**
```
UPLOAD report.pdf 45312
```

**Server Response:**
- Success: `OK: Ready to receive file`
- Error: `ERROR: <reason>`

**File Transfer:**
After receiving `OK: Ready to receive file`, the client sends the file in chunks:
- **Chunk Size**: 1024 bytes
- **Total Bytes**: Must match `<filesize>`
- **End Marker**: No explicit marker, server counts bytes

**Server Final Response:**
- Success: `OK: '<filename>' uploaded successfully (<filesize> bytes).`
- Error: `ERROR: <reason>`

---

### 2. DOWNLOAD Command

**Client to Server:**
```
DOWNLOAD <filename>
```

**Example:**
```
DOWNLOAD report.pdf
```

**Server Response:**
- File exists: `OK <filesize>`
- File not found: `ERROR: File '<filename>' not found.`

**File Transfer:**
After receiving `OK <filesize>`, the server sends the file in chunks:
- **Chunk Size**: 1024 bytes
- **Total Bytes**: Must match `<filesize>`
- **End Marker**: No explicit marker, client counts bytes

**Client Final Response:**
- Success: `Download complete: '<filename>' (<filesize> bytes)`
- Error: `ERROR: <reason>`

---

### 3. LIST Command

**Client to Server:**
```
LIST
```

**Server Response:**
```
OK
<filename1>
<filename2>
...
END
```

**Example:**
```
OK
report.pdf
image.png
data.csv
END
```

---

### 4. HELP Command

**Client to Server:**
```
HELP
```

**Server Response:**
```
OK: Available commands:
- upload <path>: Upload a file
- download <name>: Download a file
- list: List all files
- help: Show this help
- exit: Disconnect
```

---

### 5. EXIT Command

**Client to Server:**
```
EXIT
```

**Server Response:**
```
OK: Goodbye.
```

The server closes the connection after sending this response.

---

## Error Handling

### Common Error Responses
| Error | Description |
|-------|-------------|
| `ERROR: Invalid command.` | Unknown command received |
| `ERROR: Missing arguments.` | Command missing required parameters |
| `ERROR: File '<name>' not found.` | Requested file does not exist |
| `ERROR: File too large.` | File exceeds size limit |
| `ERROR: Connection timeout.` | No data received within timeout period |
| `ERROR: Internal server error.` | Unexpected error on server |

---

## State Diagrams

### Client States
```
START
  │
  ▼
CONNECT ──► CONNECTED
  │              │
  │              ▼
  │          SEND_COMMAND
  │              │
  │              ▼
  │          WAIT_RESPONSE
  │              │
  │              ▼
  └◄─── EXIT ─── CONNECTED
  │
  ▼
DISCONNECT
```

### Server States (per client)
```
WAIT_COMMAND
  │
  ▼
PARSE_COMMAND
  │
  ▼
EXECUTE_ACTION
  │
  ▼
SEND_RESPONSE
  │
  └─► (loop back to WAIT_COMMAND)
  │
  ▼
CLOSE_CONNECTION (on EXIT)
```

---

## Message Sequence Charts

### Upload Sequence
```
Client                           Server
   │                               │
   │── UPLOAD file.txt 1024 ──────►│
   │◄─ OK: Ready to receive ────────│
   │                               │
   │── <file bytes> ──────────────►│
   │                               │
   │◄─ OK: uploaded successfully ───│
   │                               │
```

### Download Sequence
```
Client                           Server
   │                               │
   │── DOWNLOAD file.txt ─────────►│
   │◄─ OK 1024 ───────────────────│
   │                               │
   │◄─ <file bytes> ───────────────│
   │                               │
```

### List Sequence
```
Client                           Server
   │                               │
   │── LIST ──────────────────────►│
   │◄─ OK                         │
   │◄─ file1.txt                  │
   │◄─ file2.txt                  │
   │◄─ END                        │
   │                               │
```

---

## Configuration Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `BUFFER_SIZE` | 4096 | Size of command buffer |
| `CHUNK_SIZE` | 1024 | Size of file transfer chunks |
| `MAX_FILE_SIZE` | 104857600 | 100MB max file size |
| `CONNECTION_TIMEOUT` | 10 | Seconds before timeout |
| `SERVER_PORT` | 5001 | Default server port |

---

## Security Considerations

1. **Filename Sanitization**: Remove path traversal characters (`../`, `\`)
2. **File Size Limits**: Prevent server disk exhaustion
3. **Connection Limits**: Limit concurrent connections per IP
4. **Timeout Handling**: Close idle connections

---

## Version History
- **v1.0**: Initial protocol specification