import bluetooth
import subprocess
import os
import sys

def edit_file_locally(sock):
    local_tmp_file = "tmp_edit.txt"
    with open(local_tmp_file, 'w') as tmp_file:
        content = sock.recv(4096).decode('utf-8')
        tmp_file.write(content)

    subprocess.run(["vim", local_tmp_file])  # Open the file with vim for editing

    with open(local_tmp_file, 'r') as tmp_file:
        edited_content = tmp_file.read()
    sock.send(edited_content.encode('utf-8'))

    response = sock.recv(1024).decode('utf-8')
    print(response)


def discover_devices():
    devices = bluetooth.discover_devices(lookup_names=True)
    return devices

def main():
    print("[+] Scanning for available Bluetooth devices...")
    devices = discover_devices()

    if not devices:
        print("[!] No devices found. Exiting")
        sys.exit(0)

    print("\n[+] Available devices:")
    for idx, (mac, name) in enumerate(devices, start=1):
        print(f"{idx}, {name} {{mac}}")

    try:
        choice = int(input("\nChoose a device to connect to (enter number):"))
        if choice < 1 or choice > len(devices):
            raise ValueError
        mac_adress, device_name = devices[choice - 1]
    except ValueError:
        print("[!] Invalid choice. Exiting.")
        sys.exit(1)

    bluetooth_client(mac_adress)

def bluetooth_client(server_mac_address, port=1):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    print(f"[+] Connecting to {server_mac_address}...")
    sock.connect((server_mac_address, port))
    print("[+] Connected!")

    try:
        while True:
            cmd = input(">> ")
            if cmd.lower() == "exit":
                print("[+] Exiting client...")
                break

            sock.sendall(cmd.encode('utf-8'))

            if cmd.startswith("edit_file "):
                edit_file_locally(sock)
            else:
                response = sock.recv(1024).decode('utf-8')
                print(f"{response.strip()}")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()

    #server_mac_address = "E4:5F:01:5C:15:C4"  # Server's Bluetooth MAC address
    #bluetooth_client(server_mac_address)

