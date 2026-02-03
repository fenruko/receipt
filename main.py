import sys
import os
import subprocess
import tkinter as tk

# Redirect output if no console (for PyInstaller --noconsole)
# This prevents crashes when "print" is called in a no-console environment
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

def install_requirements():
    """
    Installs requirements.txt if running from source (not frozen).
    """
    # Check if running as a PyInstaller bundle (frozen)
    if getattr(sys, 'frozen', False):
        return

    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(requirements_file):
        return

    try:
        # Configure startup info to hide console window during pip install
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file, "--quiet"],
            startupinfo=startupinfo,
            stdout=open(os.devnull, 'w'),
            stderr=open(os.devnull, 'w')
        )
    except Exception:
        # Fail silently or log to file if needed
        pass

if __name__ == "__main__":
    # Ensure dependencies are installed (dev mode only)
    install_requirements()

    # Move imports here to ensure packages are available after install
    try:
        from gui import ReceiptApp
    except ImportError:
        # Fallback if install failed or something is wrong
        # We can try to show a message box using raw ctypes or basic tk
        pass

    root = tk.Tk()
    app = ReceiptApp(root)
    root.mainloop()