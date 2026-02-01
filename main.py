import tkinter as tk
from gui import ReceiptApp

if __name__ == "__main__":
    root = tk.Tk()
    # Optional: Set icon or theme
    try:
        # Increase DPI awareness on Windows for sharper text
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = ReceiptApp(root)
    root.mainloop()
