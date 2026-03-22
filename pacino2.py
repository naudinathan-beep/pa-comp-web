import tkinter as tk
import socket
import os
import struct
import threading
from PIL import Image, ImageTk


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



review_images = []
wega_images = []
danger_images = []



class PACompApp:

    def __init__(self, root):
        self.root = root
        root.title("PA Comp")
        root.geometry("1200x700")

        self.pages = {}

        for Page in (HomePage, GalleryPage, InfoPage):
            page = Page(root, self)
            self.pages[Page.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.show_page("HomePage")

    def show_page(self, name, data=None):
        page = self.pages[name]
        if hasattr(page, "load_data"):
            page.load_data(data)
        page.tkraise()



class HomePage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="PA Comp", font=("Arial", 24)).pack(pady=10)

       
        btn_frame = tk.Frame(self)
        btn_frame.pack()

        tk.Button(btn_frame, text="WEGA", bg="green",
                  command=lambda: app.show_page("GalleryPage", wega_images)).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="REVIEW", bg="yellow",
                  command=lambda: app.show_page("GalleryPage", review_images)).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="DANGER", bg="red",
                  command=lambda: app.show_page("GalleryPage", danger_images)).grid(row=0, column=2, padx=5)

        tk.Button(btn_frame, text="INFO", bg="blue",
                  command=lambda: app.show_page("InfoPage")).grid(row=0, column=3, padx=5)

        
        self.review_frame = tk.Frame(self, bg="black")
        self.review_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.status = tk.Label(self, text="Idle")
        self.status.pack()

        tk.Button(self, text="Start Receiving",
                  command=lambda: threading.Thread(
                      target=run_client,
                      args=(self,),
                      daemon=True
                  ).start()).pack(pady=5)

    def add_review_image(self, filepath):
        img = Image.open(filepath)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)

        lbl = tk.Label(self.review_frame, image=photo, bg="black")
        lbl.image = photo
        lbl.pack(side="left", padx=5)


        lbl.bind("<Button-1>", lambda e, p=filepath: self.classify_popup(p))

    def classify_popup(self, path):
        win = tk.Toplevel(self)
        win.title("Classify Image")

        tk.Label(win, text="Choose category").pack(pady=10)

        tk.Button(win, text="WEGA", bg="green",
                  command=lambda: self.move_image(path, wega_images, win)).pack(fill="x")

        tk.Button(win, text="REVIEW", bg="yellow",
                  command=lambda: self.move_image(path, review_images, win)).pack(fill="x")

        tk.Button(win, text="DANGER", bg="red",
                  command=lambda: self.move_image(path, danger_images, win)).pack(fill="x")

    def move_image(self, path, target_list, win):
        target_list.append(path)
        win.destroy()



class GalleryPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Button(self, text="⬅ Back",
                  command=lambda: app.show_page("HomePage")).pack(anchor="nw")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

    def load_data(self, images):
        for w in self.container.winfo_children():
            w.destroy()

        if not images:
            tk.Label(self.container, text="No images here").pack()
            return

        for path in images:
            img = Image.open(path)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(self.container, image=photo)
            lbl.image = photo
            lbl.pack(side="left", padx=5, pady=5)



class InfoPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)

        tk.Button(self, text="⬅ Back",
                  command=lambda: app.show_page("HomePage")).pack(anchor="nw")

        text = """
HOW TO USE PA Comp

• Incoming images appear on the home screen
• Images will be classified by the AI
• WEGA = Safe
• REVIEW = Needs checking
• DANGER = Serious issue
• Use buttons at top to view stored images
"""

        tk.Label(self, text=text, justify="left", font=("Arial", 14)).pack(pady=50)

def run_client(home_page):

    HOST = "192.168.1.148"
    PORT = 2012

    os.makedirs("taken_images", exist_ok=True)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            inf_type_flag = 2

            home_page.status.config(text="Connected")

            while True:
                data = recv_msg(s)
                if not data:
                    break

                if inf_type_flag == 2:
                    inf_type_flag = 0
                    send_msg(s, b"images")

                elif inf_type_flag == 0:
                    filename = f"taken_images/IMG{len(os.listdir('taken_images'))}.jpg"
                    with open(filename, "wb") as f:
                        f.write(data)

                   
                    home_page.add_review_image(filename)

                    inf_type_flag = 1
                    send_msg(s, b"info")

                else:
                    inf_type_flag = 2

    except Exception as e:
        home_page.status.config(text=f"Error: {e}")


root = tk.Tk()
app = PACompApp(root)
root.mainloop()
