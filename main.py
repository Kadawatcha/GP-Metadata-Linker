import tkinter as tk
from gui import PhotoMetadataApp
import ctypes


ctypes.windll.shcore.SetProcessDpiAwareness(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoMetadataApp(root)
    root.mainloop()