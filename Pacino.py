import tkinter as tk
import socket
import os
import struct
import threading


def recvall(c, n):
    data = bytearray()
    while len(data) < n:
        packet = c.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)

def send_msg(c, data):
    c.sendall(struct.pack('>I', len(data)) + data)

def recv_msg(c):
    raw_len = recvall(c, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack('>I', raw_len)[0]
    return recvall(c, msg_len)


def run_client(status_label):
    HOST = ""  
    PORT = 2012

    os.makedirs("taken_images", exist_ok=True)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            inf_type_flag = 2

            status_label.config(text="Connected to server")

            while True:
                data = recv_msg(s)
                if not data:
                    break

                if inf_type_flag == 2:
                    inf_type_flag = 0
                    send_msg(s, b"images")
                    status_label.config(text="Requesting images...")

                elif inf_type_flag == 0:
                    filename = f"taken_images/IMG{len(os.listdir('taken_images'))}.jpg"
                    with open(filename, "wb") as f:
                        f.write(data)

                    inf_type_flag = 1
                    send_msg(s, b"info")
                    status_label.config(text=f"Image saved: {filename}")

                else:
                    with open("info.txt", "a") as f:
                        f.write(data.decode('utf-8') + "\n")

                    send_msg(s, b"end")
                    inf_type_flag = 2
                    status_label.config(text="Info saved")

    except Exception as e:
        status_label.config(text=f"Error: {e}")


root = tk.Tk()
root.title("PA Comp")
root.geometry("600x450")

title = tk.Label(root, text="PA Comp", font=("Arial", 20))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack(expand=True, fill="both", padx=10, pady=10)

def create_category(parent, text, color):
    box = tk.Frame(parent, bg=color, width=250, height=150)
    box.pack_propagate(False)
    label = tk.Label(box, text=text, bg=color, font=("Arial", 16, "bold"))
    label.pack(expand=True)
    return box


wega = create_category(frame, "WEGA", "green")
review = create_category(frame, "REVIEW", "yellow")
danger = create_category(frame, "DANGER", "red")
info = create_category(frame, "INFO", "blue")

wega.grid(row=0, column=0, padx=10, pady=10)
review.grid(row=0, column=1, padx=10, pady=10)
danger.grid(row=1, column=0, padx=10, pady=10)
info.grid(row=1, column=1, padx=10, pady=10)


status_label = tk.Label(root, text="Idle", font=("Arial", 12))
status_label.pack(pady=5)


start_button = tk.Button(
    root,
    text="Start Receiving",
    font=("Arial", 12),
    command=lambda: threading.Thread(
        target=run_client,
        args=(status_label,),
        daemon=True
    ).start()
)
start_button.pack(pady=10)

root.mainloop()
