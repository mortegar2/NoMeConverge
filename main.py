import tkinter as tk
from src.interfaz.app_principal import AppPrincipal

if __name__ == "__main__":
    root = tk.Tk()
    app = AppPrincipal(root)
    root.mainloop()