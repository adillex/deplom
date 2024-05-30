import socket
import os
from cryptography.fernet import Fernet

# Generate and save an encryption key
def generate_key():
    key = Fernet.generate_key()
    with open("server_key.key", "wb") as key_file:
        key_file.write(key)
    return key

# Load the encryption key from a file
def load_key():
    return open("server_key.key", "rb").read()

# Verify and authorize the STL file
def verify_and_authorize(file_path, cipher):
    with open(file_path, 'rb') as file:
        data = file.read()
    encrypted_data = cipher.encrypt(data)
    return encrypted_data

def start_server(host='0.0.0.0', port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f'Server started on {host}:{port}. Waiting for connections...')

    while True:
        conn, addr = s.accept()
        print(f'Connected by {addr}')

        # Generate a new encryption key for each session
        key = generate_key()
        conn.sendall(key)
        
        # Receive verification request from the client
        verification_request = conn.recv(1024)
        if verification_request.decode() == 'verify':
            # Send the executable verification code to the client
            with open("verification_code.py", "rb") as f:
                code = f.read()
                conn.sendall(code)
            print("Verification code sent to the client.")

        # Receive the encrypted STL file from the client
        encrypted_data = b""
        while True:
            part = conn.recv(1024)
            if not part:
                break
            encrypted_data += part

        # Save the received encrypted STL file
        with open("encrypted_stl_file.stl", "wb") as f:
            f.write(encrypted_data)

        print("Encrypted STL file received and saved.")

        # Decrypt the received STL file
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)

        # Save the decrypted STL file
        with open("received_stl_file.stl", "wb") as f:
            f.write(decrypted_data)

        print("STL file decrypted and saved.")

        # Send confirmation to the client
        conn.sendall(b'file received and decrypted')

        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    start_server()
