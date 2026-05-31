"""
AppPrincipal

Ventana principal de la aplicación de Métodos Numéricos.

Responsabilidades:
- Configurar ventana principal
- Definir estilo visual
- Gestionar pestañas (módulos)
- Cargar vistas de la aplicación
"""

import tkinter as tk
from tkinter import ttk

from src.interfaz.vistas.vista_raices import VistaRaices
from src.interfaz.vistas.vista_interpolacion import VistaInterpolacion
from src.interfaz.vistas.vista_sistemas_lineales import VistaSistemasLineales
from src.interfaz.vistas.vista_integracion_derivacion import VistaIntegracionDerivacion
from src.interfaz.vistas.vista_ecuaciones_diferenciales import VistaEcuacionesDiferenciales


class AppPrincipal:
    """
    Clase principal de la aplicación.

    Actúa como contenedor de módulos (pestañas).
    """

    def __init__(self, root):
        self.root = root

        # Configuración base de la ventana
        self.root.title("Métodos Numéricos")
        self.root.geometry("1200x600")

        self._configurar_estilos()
        self._crear_notebook()
        self._cargar_modulos()

    # =========================================================
    # ESTILOS VISUALES
    # =========================================================
    def _configurar_estilos(self):
        """
        Define el tema y estilos generales de la interfaz.
        """

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TLabelFrame", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    # =========================================================
    # CONTENEDOR DE PESTAÑAS
    # =========================================================
    def _crear_notebook(self):
        """
        Crea el sistema de pestañas (tabs) de la aplicación.
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=10)

    # =========================================================
    # CARGA DE MÓDULOS
    # =========================================================
    def _cargar_modulos(self):
        """
        Inicializa y agrega los módulos principales a la interfaz.
        """

        # -------------------------
        # MÓDULO: Cálculo de raíces
        # -------------------------
        tab_raices = ttk.Frame(self.notebook)
        self.notebook.add(tab_raices, text="Cálculo de raíces")

        VistaRaices(tab_raices)

        # -------------------------
        # MÓDULO: Interpolación
        # -------------------------
        tab_interpolacion = ttk.Frame(self.notebook)
        self.notebook.add(tab_interpolacion, text="Interpolación")

        VistaInterpolacion(tab_interpolacion)
        # -------------------------
        # Módulo: Sistemas lineales
        # -------------------------
        tab_sistemas = ttk.Frame(self.notebook)
        self.notebook.add(tab_sistemas, text="Sistemas lineales")

        VistaSistemasLineales(tab_sistemas)

        # -------------------------
        # Módulo: Integración y derivación
        # -------------------------
        tab_integracion = ttk.Frame(self.notebook)
        self.notebook.add(tab_integracion, text="Integración y derivación")

        VistaIntegracionDerivacion(tab_integracion)

        # -------------------------
        # Módulo: Ecuaciones diferenciales
        # -------------------------
        tab_ecuaciones = ttk.Frame(self.notebook)
        self.notebook.add(tab_ecuaciones, text="Ecuaciones diferenciales")

        VistaEcuacionesDiferenciales(tab_ecuaciones)