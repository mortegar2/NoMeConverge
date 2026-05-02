"""
VistaRaices
Interfaz gráfica para métodos numéricos de raíces (versión simplificada)
- SIN tabla de iteraciones
- SOLO procedimiento paso a paso
- PDF con mejor presentación (márgenes visuales)
"""

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT

from src.algoritmos.raices import biseccion, newton_raphson, secante
from src.utilidades.excepciones import MetodosNumericosError
from src.utilidades.evaluador_funciones import EvaluadorFunciones


class VistaRaices:
    """
    Interfaz gráfica para el cálculo de raíces de funciones utilizando métodos numéricos.

    Esta clase crea una interfaz de usuario que permite al usuario ingresar parámetros
    para los métodos de bisección, Newton-Raphson y secante, visualizar el procedimiento
    paso a paso, mostrar una gráfica de la función y exportar resultados a PDF.

    Attributes:
        parent (tk.Frame): Frame contenedor donde se construye la interfaz.
        ultimo_resultado (dict): Almacena el resultado del último cálculo realizado.
    """

    def __init__(self, parent_frame):
        """
        Inicializa la vista de raíces.

        Args:
            parent_frame (tk.Frame): Frame padre donde se construirá la interfaz.
        """
        self.parent = parent_frame
        self.ultimo_resultado = None
        self._crear_ui()

    def _crear_ui(self):
        """
        Construye la interfaz de usuario completa.

        Configura el layout principal con grid, crea los paneles de parámetros,
        ayuda, procedimiento y gráfica, y establece los controles interactivos.
        """
        self.parent.grid_rowconfigure(0, weight=2)
        self.parent.grid_rowconfigure(1, weight=3)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        # =========================
        # PANEL IZQUIERDO
        # =========================
        ctrl = ttk.Labelframe(self.parent, text="Parámetros")
        ctrl.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.var_f = tk.StringVar(value="x**3 - x - 2")

        ttk.Label(ctrl, text="f(x) =").grid(row=0, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_f).grid(row=0, column=1)

        self.var_met = tk.StringVar(value="Bisección")

        ttk.Label(ctrl, text="Método").grid(row=1, column=0, sticky="w")

        combo = ttk.Combobox(
            ctrl,
            textvariable=self.var_met,
            values=["Bisección", "Newton-Raphson", "Secante"],
            state="readonly"
        )
        combo.grid(row=1, column=1)
        combo.bind("<<ComboboxSelected>>", self._ajustar_campos)

        self._crear_campos(ctrl)

        self.var_tol = tk.StringVar(value="1e-6")
        self.var_max = tk.StringVar(value="100")

        ttk.Label(ctrl, text="Tolerancia").grid(row=4, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_tol).grid(row=4, column=1)

        ttk.Label(ctrl, text="Max Iter").grid(row=5, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_max).grid(row=5, column=1)

        frame_btn = ttk.Frame(ctrl)
        frame_btn.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(frame_btn, text="Calcular", command=self._ejecutar).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="PDF", command=self._exportar_pdf).pack(side="left", padx=5)

        self.lbl_resultado = ttk.Label(ctrl, text="")
        self.lbl_resultado.grid(row=7, column=0, columnspan=2)

        self._ajustar_campos(None)

        # =========================
        # AYUDA
        # =========================
        help_frame = ttk.Labelframe(self.parent, text="Guía de funciones")
        help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        tree_help = ttk.Treeview(help_frame, columns=("func", "ejemplo"), show="headings")
        tree_help.heading("func", text="Función")
        tree_help.heading("ejemplo", text="Ejemplo")

        for d in [
            ("sin(x)", "sin(x) - 0.5"),
            ("cos(x)", "cos(x) - x"),
            ("exp(x)", "exp(x) - 2"),
            ("log(x)", "log(x) + x - 2"),
            ("Polinomios", "x**3 - x - 2")
        ]:
            tree_help.insert("", "end", values=d)

        tree_help.pack(fill="both", expand=True)

        # =========================
        # PROCEDIMIENTO
        # =========================
        frame_proc = ttk.Labelframe(self.parent, text="Procedimiento Paso a Paso")
        frame_proc.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_proc.grid_columnconfigure(0, weight=1)
        frame_proc.grid_rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame_proc)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.text_proc = tk.Text(
            frame_proc,
            wrap="word",
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )
        self.text_proc.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.text_proc.yview)

        # =========================
        # GRÁFICA
        # =========================
        frame_graf = ttk.Frame(self.parent)
        frame_graf.grid(row=1, column=1, sticky="nsew")

        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graf)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _crear_campos(self, ctrl):
        """
        Crea los widgets para los parámetros específicos de cada método.

        Inicializa las variables de control y los labels/entries para a, b, x0, x1,
        que se mostrarán/ocultarán según el método seleccionado.

        Args:
            ctrl (ttk.LabelFrame): Frame contenedor donde agregar los campos.
        """
        self.var_a = tk.StringVar(value="1")
        self.var_b = tk.StringVar(value="2")
        self.var_x0 = tk.StringVar(value="1.5")
        self.var_x1 = tk.StringVar(value="2")

        self.lbl_a = ttk.Label(ctrl, text="a")
        self.ent_a = ttk.Entry(ctrl, textvariable=self.var_a)

        self.lbl_b = ttk.Label(ctrl, text="b")
        self.ent_b = ttk.Entry(ctrl, textvariable=self.var_b)

        self.lbl_x0 = ttk.Label(ctrl, text="x0")
        self.ent_x0 = ttk.Entry(ctrl, textvariable=self.var_x0)

        self.lbl_x1 = ttk.Label(ctrl, text="x1")
        self.ent_x1 = ttk.Entry(ctrl, textvariable=self.var_x1)

    def _ajustar_campos(self, e):
        """
        Muestra/oculta los campos de parámetros según el método seleccionado.

        Para bisección: muestra a y b.
        Para Newton-Raphson: muestra x0.
        Para secante: muestra x0 y x1.

        Args:
            e: Evento del combobox (no utilizado).
        """
        for w in [self.lbl_a, self.ent_a, self.lbl_b, self.ent_b,
                  self.lbl_x0, self.ent_x0, self.lbl_x1, self.ent_x1]:
            w.grid_remove()

        m = self.var_met.get()

        if m == "Bisección":
            self.lbl_a.grid(row=2, column=0)
            self.ent_a.grid(row=2, column=1)
            self.lbl_b.grid(row=3, column=0)
            self.ent_b.grid(row=3, column=1)

        elif m == "Newton-Raphson":
            self.lbl_x0.grid(row=2, column=0)
            self.ent_x0.grid(row=2, column=1)

        else:
            self.lbl_x0.grid(row=2, column=0)
            self.ent_x0.grid(row=2, column=1)
            self.lbl_x1.grid(row=3, column=0)
            self.ent_x1.grid(row=3, column=1)

    def _ejecutar(self):
        try:
            f = EvaluadorFunciones.crear_funcion_univariable(self.var_f.get())

            tol = float(self.var_tol.get())
            max_iter = int(self.var_max.get())
            metodo = self.var_met.get()

            self.text_proc.config(state="normal")
            self.text_proc.delete("1.0", "end")

            if metodo == "Bisección":
                res = biseccion(f, float(self.var_a.get()), float(self.var_b.get()), tol, max_iter)
            elif metodo == "Newton-Raphson":
                res = newton_raphson(f, float(self.var_x0.get()), tol, max_iter)
            else:
                res = secante(f, float(self.var_x0.get()), float(self.var_x1.get()), tol, max_iter)

            self.ultimo_resultado = res

            self._mostrar_procedimiento(metodo, res)

            # =========================
            # GRAFICA MEJORADA
            # =========================
            raiz = res["raiz"]

            escala = max(3, abs(raiz) * 2)
            x_min = raiz - escala
            x_max = raiz + escala

            x = np.linspace(x_min, x_max, 1200)
            y = np.array([f(val) for val in x])

            # FILTRAR valores NaN e infinitos (para log(x), sqrt(x), etc.)
            mascara_valida = np.isfinite(y)
            x_valida = x[mascara_valida]
            y_valida = y[mascara_valida]

            # Si todos los valores son NaN, usar el rango sin filtrar
            if len(x_valida) == 0:
                x_valida = x
                y_valida = y

            # Evitar explosiones visuales
            y_clipped = np.clip(y_valida, -50, 50)
            y_min = np.min(y_clipped)
            y_max = np.max(y_clipped)

            margen_y = (y_max - y_min) * 0.1 if (y_max - y_min) > 0 else 1

            # LIMPIAR UNA SOLA VEZ
            self.ax.clear()

            # Fondo estilo matemático
            self.ax.set_facecolor("#fafafa")

            # Límites - usar solo valores válidos para el rango x
            if len(x_valida) > 0:
                x_min_plot = np.min(x_valida)
                x_max_plot = np.max(x_valida)
            else:
                x_min_plot = x_min
                x_max_plot = x_max

            self.ax.set_xlim(x_min_plot, x_max_plot)
            self.ax.set_ylim(y_min - margen_y, y_max + margen_y)

            # Curva - solo con puntos válidos
            self.ax.plot(x_valida, y_clipped, color="#1f77b4", linewidth=2, label="f(x)")

            # Ejes principales
            self.ax.axhline(0, color="black", linewidth=1.5, alpha=0.8)
            self.ax.axvline(0, color="black", linewidth=1.5, alpha=0.8)

            # GRID limpio (solo una versión)
            self.ax.grid(True, which="major", linestyle="--", alpha=0.6)
            self.ax.grid(True, which="minor", linestyle=":", alpha=0.3)

            # Raíz destacada
            self.ax.scatter(
                raiz,
                f(raiz),
                s=100,
                color="#d62728",
                edgecolors="darkred",
                linewidth=2,
                zorder=5,
                label=f"Raíz: {raiz:.4f}"
            )

            # Títulos
            self.ax.set_title(f"Método: {metodo}", fontsize=12, fontweight="bold")
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("f(x)")

            self.ax.legend()

            self.canvas.draw()

            self.lbl_resultado.config(
                text=f"Raíz: {raiz:.6f} | Iteraciones: {res['iteraciones']}"
            )

            self.text_proc.config(state="disabled")

        except MetodosNumericosError as e:
            messagebox.showwarning("Error", str(e))
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error Detallado", error_msg)

    def _mostrar_procedimiento(self, metodo, resultado):
        """
        Muestra el procedimiento paso a paso en el widget de texto.

        Args:
            metodo (str): Nombre del método utilizado.
            resultado (dict): Diccionario con 'historial' y 'raiz'.
        """
        text = self.text_proc
        text.insert("end", f"MÉTODO: {metodo}\n\n")

        for h in resultado["historial"]:
            text.insert("end", h["detalle"] + "\n")

        text.insert("end", f"\nRAÍZ FINAL: {resultado['raiz']}\n")

    def _exportar_pdf(self):
        """
        Exporta el procedimiento y resultado a un archivo PDF.

        Utiliza ReportLab para crear un documento con el método utilizado,
        los pasos del procedimiento y la raíz final. El archivo se guarda
        como 'raices.pdf' en el directorio actual.
        """
        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Primero calcula")
            return

        doc = SimpleDocTemplate(
            "raices.pdf",
            pagesize=letter,
            leftMargin=60,
            rightMargin=60,
            topMargin=60,
            bottomMargin=60
        )

        estilos = getSampleStyleSheet()

        estilo_texto = ParagraphStyle(
            "custom",
            parent=estilos["Normal"],
            alignment=TA_LEFT,
            fontSize=10,
            leading=14
        )

        contenido = []

        def t(x):
            contenido.append(Paragraph(x, estilo_texto))
            contenido.append(Spacer(1, 8))

        t("<b>MÉTODO:</b> " + self.var_met.get())

        for h in self.ultimo_resultado["historial"]:
            t(h["detalle"])

        t(f"<b>RAÍZ:</b> {self.ultimo_resultado['raiz']}")

        doc.build(contenido)

        messagebox.showinfo("PDF", "Generado correctamente")