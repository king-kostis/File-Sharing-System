#!/usr/bin/env python3
"""
File-Sharing System - Client
Network & Distributed Programming — Group 4 Project
"""

import socket
import os
import os.path

# Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
DOWNLOAD_DIR = "client_downloads/"
BUFFER_SIZE = 4096
CHUNK_SIZE = 1024


def ensure_download_dir():
    """Create download directory if it doesn't exist."""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"[CLIENT] Download directory created: {DOWNLOAD_DIR}")


def connect_to_server():
    """Connect to the server and return the socket."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CLIENT] Connected to server at {SERVER_HOST}:{SERVER_PORT}")
        return client_socket
    except Exception as e:
        print(f"[CLIENT] Connection failed: {e}")
        return None


def upload_file(client_socket, filepath):
    """Upload a file to the server."""
    if not os.path.exists(filepath):
        print(f"[CLIENT] Error: File '{filepath}' not found.")
        return
    
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    
    # Send upload command
    command = f"UPLOAD {filename} {filesize}\n"
    client_socket.sendall(command.encode('utf-8'))
    
    # Wait for acknowledgment
    response = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
    
    if not response.startswith("OK"):
        print(f"[CLIENT] {response}")
        return
    
    # Send file data
    try:
        with open(filepath, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < filesize:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                client_socket.sendall(chunk)
                bytes_sent += len(chunk)
        
        # Get final response
        response = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
        print(f"[CLIENT] {response}")
    
    except Exception as e:
        print(f"[CLIENT] Error uploading file: {e}")


def download_file(client_socket, filename):
    """Download a file from the server."""
    # Send download command
    command = f"DOWNLOAD {filename}\n"
    client_socket.sendall(command.encode('utf-8'))
    
    # Get file size acknowledgment
    response = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
    
    if not response.startswith("OK"):
        print(f"[CLIENT] {response}")
        return
    
    try:
        filesize = int(response.split()[1])
    except (IndexError, ValueError):
        print("[CLIENT] Error: Invalid file size response")
        return
    
    # Receive file data
    try:
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            bytes_received = 0
            while bytes_received < filesize:
                chunk = client_socket.recv(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
        
        if bytes_received == filesize:
            print(f"[CLIENT] Download complete: '{filepath}' ({filesize} bytes)")
        else:
            print("[CLIENT] Error: Incomplete file transfer")
    
    except Exception as e:
        print(f"[CLIENT] Error downloading file: {e}")


def list_files(client_socket):
    """List files available on the server."""
    # Send list command
    command = "LIST\n"
    client_socket.sendall(command.encode('utf-8'))
    
    # Get file list
    response = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
    
    if response.startswith("OK"):
        lines = response.split('\n')
        if len(lines) > 1:
            print("[SERVER] Files available:")
            for line in lines[1:]:
                if line and line != "END":
                    print(f"  • {line}")
        else:
            print("[SERVER] No files available.")
    else:
        print(f"[CLIENT] {response}")


def show_help(client_socket):
    """Show help from server."""
    command = "HELP\n"
    client_socket.sendall(command.encode('utf-8'))
    
    response = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
    print(f"[SERVER] {response}")


def main():
    """Main client function."""
    ensure_download_dir()
    
    client_socket = connect_to_server()
    if not client_socket:
        return
    
    try:
        while True:
            try:
                command = input(">>> ").strip()
            except EOFError:
                break
            
            if not command:
                continue
            
            parts = command.split(" ", 1)
            cmd = parts[0].lower()
            
            if cmd == "upload":
                filepath = parts[1].strip("'\"")
                if len(parts) < 2:
                    print("[CLIENT] Usage: upload <filepath>")
                else:
                    upload_file(client_socket, filepath)
            
            elif cmd == "download":
                if len(parts) < 2:
                    print("[CLIENT] Usage: download <filename>")
                else:
                    download_file(client_socket, parts[1])
            
            elif cmd == "list":
                list_files(client_socket)
            
            elif cmd == "help":
                show_help(client_socket)
            
            elif cmd == "exit":
                client_socket.sendall(b"EXIT\n")
                response = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
                print(f"[SERVER] {response}")
                break
            
            else:
                print(f"[CLIENT] Unknown command: {cmd}")
                print("[CLIENT] Type 'help' for available commands")
    
    except KeyboardInterrupt:
        print("\n[CLIENT] Disconnecting...")
    
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()