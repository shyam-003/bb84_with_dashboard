# main.py
import tkinter as tk
from gui import QKDApp

def main():
    root = tk.Tk()
    app = QKDApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()