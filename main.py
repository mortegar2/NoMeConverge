import tkinter as tk

from src.interfaz.app_principal import AppPrincipal


def main():
    root = tk.Tk()
    AppPrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
