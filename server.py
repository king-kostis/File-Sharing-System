#!/usr/bin/env python3
"""
File-Sharing System - Server
Network & Distributed Programming: Group 4 Project
"""

import socket
import threading
import os
import os.path

# Configuration
HOST = "0.0.0.0"
PORT = 5001
STORAGE_DIR = "server_storage/"
MAX_CLIENTS = 5
BUFFER_SIZE = 4096
CHUNK_SIZE = 1024

# Thread lock for file operations
file_lock = threading.Lock()


def ensure_storage_dir():
    """Create storage directory if it doesn't exist."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
        print(f"[SERVER] Storage directory created: {STORAGE_DIR}")


def handle_client(client_socket, client_address):
    """Handle a single client connection."""
    print(f"[SERVER] Connection from {client_address}")
    
    try:
        while True:
            # Receive command
            command = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
            
            if not command:
                break
            
            parts = command.split(" ", 2)
            
            if not parts:
                continue
            
            cmd = parts[0].upper()
            
            if cmd == "UPLOAD":
                handle_upload(client_socket, parts)
            elif cmd == "DOWNLOAD":
                handle_download(client_socket, parts)
            elif cmd == "LIST":
                handle_list(client_socket)
            elif cmd == "HELP":
                handle_help(client_socket)
            elif cmd == "EXIT":
                client_socket.sendall(b"OK: Goodbye.\n")
                print(f"[SERVER] Client {client_address} disconnected")
                break
            else:
                client_socket.sendall(b"ERROR: Invalid command.\n")
    
    except Exception as e:
        print(f"[SERVER] Error handling client {client_address}: {e}")
    
    finally:
        client_socket.close()


def handle_upload(client_socket, parts):
    """Handle file upload from client."""
    if len(parts) < 3:
        client_socket.sendall(b"ERROR: Missing arguments.\n")
        return
    
    try:
        filesize = int(parts[1])
    except ValueError:
        client_socket.sendall(b"ERROR: Invalid file size.\n")
        return
    filename = " ".join(parts[2:])
    
    # Sanitize filename
    filename = os.path.basename(filename)
    
    # Check file size limit (100MB)
    if filesize > 104857600:
        client_socket.sendall(b"ERROR: File too large.\n")
        return
    
    filepath = os.path.join(STORAGE_DIR, filename)
    
    # Acknowledge ready to receive
    client_socket.sendall(b"OK: Ready to receive file\n")
    
    try:
        with file_lock:
            with open(filepath, 'wb') as f:
                bytes_received = 0
                while bytes_received < filesize:
                    chunk = client_socket.recv(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_received += len(chunk)
        
        if bytes_received == filesize:
            client_socket.sendall(f"OK: '{filename}' uploaded successfully ({filesize} bytes).\n".encode('utf-8'))
            print(f"[SERVER] File '{filename}' uploaded ({filesize} bytes)")
        else:
            client_socket.sendall(b"ERROR: Incomplete file transfer.\n")
    
    except Exception as e:
        client_socket.sendall(f"ERROR: {str(e)}\n".encode('utf-8'))


def handle_download(client_socket, parts):
    """Handle file download request from client."""
    if len(parts) < 2:
        client_socket.sendall(b"ERROR: Missing arguments.\n")
        return
    
    filename = " ".join(parts[1:])
    filepath = os.path.join(STORAGE_DIR, filename)
    
    if not os.path.exists(filepath):
        client_socket.sendall(f"ERROR: File '{filename}' not found.\n".encode('utf-8'))
        return
    
    filesize = os.path.getsize(filepath)
    
    # Send file size acknowledgment
    client_socket.sendall(f"OK {filesize}\n".encode('utf-8'))
    
    try:
        with file_lock:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
        
        print(f"[SERVER] File '{filename}' downloaded by client")
    
    except Exception as e:
        client_socket.sendall(f"ERROR: {str(e)}\n".encode('utf-8'))


def handle_list(client_socket):
    """Handle file list request from client."""
    try:
        files = os.listdir(STORAGE_DIR)
        response = "OK\n"
        for f in files:
            response += f + "\n"
        response += "END\n"
        client_socket.sendall(response.encode('utf-8'))
    except Exception as e:
        client_socket.sendall(f"ERROR: {str(e)}\n".encode('utf-8'))


def handle_help(client_socket):
    """Send help information to client."""
    help_text = """OK: Available commands:
- upload <path>: Upload a file
- download <name>: Download a file
- list: List all files
- help: Show this help
- exit: Disconnect
"""
    client_socket.sendall(help_text.encode('utf-8'))


def main():
    """Main server function."""
    ensure_storage_dir()
    
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        print(f"[SERVER] Starting file-sharing server on {HOST}:{PORT}")
        print(f"[SERVER] Storage directory: {STORAGE_DIR}")
        print(f"[SERVER] Waiting for connections...")
        
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()