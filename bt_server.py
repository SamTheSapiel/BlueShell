
import bluetooth
import subprocess
import threading
import os

def send_file_content(client_sock, filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        client_sock.sendall(content.encode('utf-8'))
    except Exception as e:
        client_sock.sendall(f"[!] Error reading file: {e}".encode('utf-8'))

def receive_file_content(client_sock, filepath):
    try:
        content = client_sock.recv(4096).decode('utf-8')
        with open(filepath, 'w') as f:
            f.write(content)
        client_sock.sendall("[!] File successfully saved.".encode('utf-8'))
    except Exception as e:
        client_sock.sendall(f"[!] Error writing to file: {e}".encode('utf-8'))

COMMANDS = {
    'ls': 'List all files and directories in the current directory.',
    'cat': 'Display the content of a file. Usage: cat <filename>',
    'pwd': 'Print the current working directory.',
    'echo': 'Display a message. Usage: echo <message>',
    'date': 'Display the current date and time.',
    'edit_file': 'Edit a file. Usage: edit_file <filename>',
    'cd': 'Change directory. Usage: cd <path>',
    'help': 'Display this help menu.',
    'cp': 'Copy a file or directory. Usage: cp <source> <destination>',
    'mv': 'Move or rename a file or directory. Usage: mv <source> <destination>'
}

ALLOWED_COMMANDS = set(COMMANDS.keys())

def handle_client(client_sock, client_address):
    print(f"[+] Handling client: {client_address}")
    
    current_directory = None
    
    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break

            cmd = data.decode('utf-8').strip()
            cmd_parts = cmd.split()
            base_cmd = cmd_parts[0]
            
            

            # Special handling for the cd command
            if base_cmd == "cd":
                try:
                    target_directory = cmd.split(maxsplit=1)[1]
                    os.chdir(target_directory)
                    current_directory = os.getcwd()
                    response = f"[*] Changed directory to {current_directory}\n"
                except Exception as e:
                    response = str(e) + "\n"
                client_sock.sendall(response.encode('utf-8'))
                continue

            # Special handling for the help command
            elif base_cmd == "help":
                response = "\nAvailable Commands:\n" + "-"*40 + "\n"
                for command, description in COMMANDS.items():
                    response += f"{command.ljust(10)} - {description}\n"
                response += "-"*40 + "\n"
                client_sock.sendall(response.encode('utf-8'))
                continue

            # Special handling for the edit command
            elif base_cmd == "edit_file":
                if len(cmd_parts) > 1:
                    filename = cmd_parts[1]
                    with open(filename, 'r') as f:
                        file_content = f.read()
                    client_sock.sendall(file_content.encode('utf-8'))

                    # Wait for the edited content
                    edited_content = client_sock.recv(4096).decode('utf-8')
                    with open(filename, 'w') as f:
                        f.write(edited_content)
                    response = "[*] File edited successfully."
                else:
                    response = "[!] Error: Filename is missing for edit_file command."

            # Handling for the whitelisted commands
            elif base_cmd in ALLOWED_COMMANDS:
                result = subprocess.run(cmd_parts, capture_output=True, text=True)
                response = result.stdout + result.stderr

                if not response:
                    response = "[*] Command executed successfully."

            # Handling for non-whitelisted commands
            else:
                response = f"[!] Error: Command '{base_cmd}' is not allowed."

            client_sock.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"[!] Error with client {client_address}: {e}")
    finally:
        client_sock.close()

def bluetooth_server():
    

    try:
        # Execute the bluetoothctl command
        result = subprocess.check_output(['bluetoothctl', '--', 'discoverable', 'on'], stderr=subprocess.STDOUT)
        #print(result.decode('utf-8'))

    except subprocess.CalledProcessError as e:
        # Catch the exception
        print(f"Command failed with error {e.returncode}")
        print(e.output.decode('utf-8')) # print the actual error message

    except Exception as e:
        # Catch other exceptions
        print(f"An error occurred: {e}")


    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = 1
    server_sock.bind(("", port))
    server_sock.listen(5)
    print("[+] Bluetooth server started. Waiting for connections on RFCOMM channel", port)

    try:
        while True:
            client_sock, client_info = server_sock.accept()
            print("[+] Accepted connection from", client_info)

            client_thread = threading.Thread(target=handle_client, args=(client_sock, client_info))
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[+] Stopping Bluetooth server...")
    finally:
        server_sock.close()

if __name__ == "__main__":
    bluetooth_server()

