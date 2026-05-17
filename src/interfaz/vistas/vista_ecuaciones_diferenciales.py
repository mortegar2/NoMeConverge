"""
VistaEcuacionesDiferenciales

Placeholder para el módulo de ecuaciones diferenciales.
"""

import tkinter as tk
from tkinter import ttk


class VistaEcuacionesDiferenciales:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._crear_ui()

    def _crear_ui(self):
        frame = ttk.Frame(self.parent)
        frame.pack(fill="both", expand=True)

        label = ttk.Label(frame, text="Módulo de Ecuaciones Diferenciales\n(En desarrollo)")
        label.pack(padx=20, pady=20)
