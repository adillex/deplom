import socket
import ssl
import tkinter as tk
from tkinter import filedialog
import hashlib

def get_file_hash(file_path):
    """Returns the SHA-256 hash of the file."""
    sha256 = hashlib.sha256()
    print("SHA-256 hash object created")
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    print("File hash computed")
    return sha256.hexdigest(), file_path

def main():
    server_address = ('26.91.241.9', 10023)  # Server IP address in Radmin VPN network
    print("Server address set:", server_address)

    # Create a secure connection
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    print("SSL context for client created")
    context.load_verify_locations("server.pem")
    print("SSL certificates for client loaded")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket for client created")
    with context.wrap_socket(sock, server_hostname='26.91.241.9') as ssock:
        ssock.connect(server_address)
        print("Connected to server:", server_address)

        # Request dynamic key
        ssock.sendall(b'REQUEST_KEY')
        print("Dynamic key request sent")
        dynamic_key = ssock.recv(1024).decode()
        print("Dynamic key received:", dynamic_key)

        # Select file using tkinter
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        file_name = file_path.split('/')[-1]
        print("File selected:", file_name)

        # Compute file hash
        file_hash, full_file_path = get_file_hash(file_path)
        print("File hash computed:", file_hash)

        # Send file name, file hash, and dynamic key to the server
        ssock.sendall(f'VERIFY_FILE:{file_name}:{file_hash}:{dynamic_key}'.encode())
        print("File name, file hash, and dynamic key sent")
        response = ssock.recv(1024).decode()
        print("Response from server received:", response)

        if response == 'FILE_VERIFIED':
            print("File verified, sending file...")
            with open(full_file_path, 'rb') as f:
                while True:
                    file_data = f.read(1024)
                    if not file_data:
                        break
                    ssock.sendall(file_data)
            print("File sent")
        elif response == 'INVALID_KEY':
            print("Invalid key, sending aborted")
        elif response == 'INVALID_FILE':
            print("Invalid file format, sending aborted")
        elif response == 'INVALID_DATA':
            print("Invalid data, sending aborted")
        else:
            print("Unknown response from server, sending aborted")

if __name__ == '__main__':
    main()
