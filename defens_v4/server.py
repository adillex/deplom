import socket
import ssl
import os
import hashlib
import random
import string
import signal
import sys
from datetime import datetime

def generate_dynamic_key():
    """Generates a dynamic key."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def verify_file(file_name):
    """Checks if the file is an STL file."""
    return file_name.endswith('.stl')

def signal_handler(sig, frame):
    print('Server is shutting down...')
    sys.exit(0)

def main():
    server_address = ('0.0.0.0', 10023)  # Listen on all interfaces
    download_directory = "downloads"

    # Create the downloads folder if it does not exist
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
        print(f"Downloads folder created: {download_directory}")

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    print("SSL context created")
    context.load_cert_chain(certfile="server.pem", keyfile="server.key")
    print("SSL certificates loaded")

    with context.wrap_socket(sock, server_side=True) as ssock:
        ssock.bind(server_address)
        print("Server bound to address:", server_address)
        ssock.listen(5)
        print("Server listening on", server_address)

        # Register the termination signal handler
        signal.signal(signal.SIGINT, signal_handler)
        print("Termination signal handler registered")

        while True:
            try:
                print("Waiting for connection...")
                connection, client_address = ssock.accept()
                print("Connection from", client_address)

                while True:
                    data = connection.recv(1024).decode('utf-8', errors='ignore')
                    if not data:
                        break
                    print("Data received:", data)
                    if data == 'REQUEST_KEY':
                        dynamic_key = generate_dynamic_key()
                        connection.sendall(dynamic_key.encode())
                        print("Dynamic key sent:", dynamic_key)
                    elif data.startswith('VERIFY_FILE:'):
                        parts = data.split(':')
                        if len(parts) == 4:
                            file_name = parts[1]
                            file_hash = parts[2]
                            received_key = parts[3]
                            print("File name received:", file_name)
                            print("File hash received:", file_hash)
                            print("Dynamic key received:", received_key)
                            if received_key == dynamic_key:
                                print(f"Verifying file with name: {file_name}")
                                if verify_file(file_name):
                                    connection.sendall(b'FILE_VERIFIED')
                                    print("File verified, FILE_VERIFIED sent")
                                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                                    save_path = os.path.join(download_directory, f"{timestamp}_{file_name}")
                                    print(f"Save path for file: {save_path}")
                                    with open(save_path, 'wb') as f:
                                        while True:
                                            file_data = connection.recv(1024)
                                            if not file_data:
                                                break
                                            f.write(file_data)
                                    print(f"File received and saved as {save_path}")
                                else:
                                    connection.sendall(b'INVALID_FILE')
                                    print(f"Invalid file format, expected .stl, received: {file_name[-4:]}")
                            else:
                                connection.sendall(b'INVALID_KEY')
                                print("Invalid key, INVALID_KEY sent")
                        else:
                            connection.sendall(b'INVALID_DATA')
                            print("Invalid data, INVALID_DATA sent")
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                try:
                    connection.close()
                    print("Connection closed")
                except NameError:
                    print("No connection was established, so it cannot be closed")

if __name__ == '__main__':
    main()
