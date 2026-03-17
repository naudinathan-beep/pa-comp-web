import tkinter as tk

root = tk.Tk()
root.title("Simple Gallery")
root.geometry("600x400")

# Title
title = tk.Label(root, text="Gallery Categories", font=("Arial", 20))
title.pack(pady=10)

# Container for categories
frame = tk.Frame(root)
frame.pack(expand=True, fill="both", padx=10, pady=10)

# Function to create a category box
def create_category(parent, text, color):
    box = tk.Frame(parent, bg=color, width=250, height=150)
    box.pack_propagate(False)  # Keep size fixed
    label = tk.Label(box, text=text, bg=color, font=("Arial", 16, "bold"))
    label.pack(expand=True)
    return box

# Create 4 categories in a grid
wega = create_category(frame, "WEGA", "green")
review = create_category(frame, "REVIEW", "yellow")
danger = create_category(frame, "DANGER", "red")
info = create_category(frame, "INFO", "blue")

wega.grid(row=0, column=0, padx=10, pady=10)
review.grid(row=0, column=1, padx=10, pady=10)
danger.grid(row=1, column=0, padx=10, pady=10)
info.grid(row=1, column=1, padx=10, pady=10)

root.mainloop()
