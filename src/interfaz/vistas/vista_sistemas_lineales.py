"""
VistaSistemasLineales

Placeholder para el módulo de sistemas lineales.
"""

import tkinter as tk
from tkinter import ttk


class VistaSistemasLineales:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._crear_ui()

    def _crear_ui(self):
        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True)

        label = ttk.Label(frame, text="Módulo de Sistemas Lineales\n(En desarrollo)")
        label.pack(padx=20, pady=20)
