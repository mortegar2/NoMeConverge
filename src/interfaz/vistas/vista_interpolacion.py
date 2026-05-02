"""
VistaInterpolacion
Interfaz gráfica para interpolación numérica (versión simplificada y profesional)
- SIN tabla de iteraciones
- SOLO procedimiento paso a paso
- PDF con márgenes correctos
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

from src.algoritmos.interpolacion import lagrange, newton_interpolacion


class VistaInterpolacion:

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.ultimo_resultado = None
        self._crear_ui()

    # =========================================================
    # UI
    # =========================================================
    def _crear_ui(self):

        self.parent.grid_rowconfigure(0, weight=2)
        self.parent.grid_rowconfigure(1, weight=3)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        # =========================
        # PANEL IZQUIERDO
        # =========================
        ctrl = ttk.Labelframe(self.parent, text="Parámetros")
        ctrl.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.var_x = tk.StringVar(value="1,2,3")
        self.var_y = tk.StringVar(value="2,4,9")
        self.var_eval = tk.StringVar(value="2.5")
        self.var_met = tk.StringVar(value="Lagrange")

        ttk.Label(ctrl, text="X:").grid(row=0, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_x).grid(row=0, column=1)

        ttk.Label(ctrl, text="Y:").grid(row=1, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_y).grid(row=1, column=1)

        ttk.Label(ctrl, text="Evaluar x =").grid(row=2, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_eval).grid(row=2, column=1)

        ttk.Label(ctrl, text="Método").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            ctrl,
            textvariable=self.var_met,
            values=["Lagrange", "Newton"],
            state="readonly"
        ).grid(row=3, column=1)

        frame_btn = ttk.Frame(ctrl)
        frame_btn.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(frame_btn, text="Calcular", command=self._ejecutar).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="PDF", command=self._exportar_pdf).pack(side="left", padx=5)

        self.lbl_resultado = ttk.Label(ctrl, text="")
        self.lbl_resultado.grid(row=5, column=0, columnspan=2)

        self.lbl_polinomio = ttk.Label(ctrl, text="")
        self.lbl_polinomio.grid(row=6, column=0, columnspan=2)

        # =========================
        # AYUDA
        # =========================
        help_frame = ttk.Labelframe(self.parent, text="Guía de uso")
        help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        tree = ttk.Treeview(help_frame, columns=("c1", "c2"), show="headings")
        tree.heading("c1", text="Concepto")
        tree.heading("c2", text="Ejemplo")

        for d in [
            ("X", "1,2,3"),
            ("Y", "2,4,9"),
            ("x eval", "2.5"),
            ("Métodos", "Lagrange / Newton"),
        ]:
            tree.insert("", "end", values=d)

        tree.pack(fill="both", expand=True)

        # =========================
        # PROCEDIMIENTO (SIN TABLA)
        # =========================
        frame_proc = ttk.Labelframe(self.parent, text="Procedimiento Paso a Paso")
        frame_proc.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_proc.grid_rowconfigure(0, weight=1)
        frame_proc.grid_columnconfigure(0, weight=1)

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

    # =========================================================
    def _parse(self, txt):
        return [float(v.strip()) for v in txt.split(",")]

    # =========================================================
    def _ejecutar(self):

        try:
            x_vals = self._parse(self.var_x.get())
            y_vals = self._parse(self.var_y.get())
            x_eval = float(self.var_eval.get())

            if len(x_vals) != len(y_vals):
                raise ValueError("X e Y deben tener la misma longitud")

            metodo = self.var_met.get()

            self.ax.clear()
            self.text_proc.config(state="normal")
            self.text_proc.delete("1.0", "end")

            if metodo == "Lagrange":
                res = lagrange(x_vals, y_vals, x_eval)
            else:
                res = newton_interpolacion(x_vals, y_vals, x_eval)

            self.ultimo_resultado = res

            self._mostrar_procedimiento(metodo, res)

            # =========================
            # GRÁFICA OPTIMIZADA
            # =========================
            x_min, x_max = min(x_vals), max(x_vals)
            margen = (x_max - x_min) * 0.2 if (x_max - x_min) > 0 else 1
            x_graf = np.linspace(x_min - margen, x_max + margen, 200)

            # Función de evaluación optimizada
            def eval_interpolacion(x_test):
                if metodo == "Lagrange":
                    return lagrange(x_vals, y_vals, x_test)["valor"]
                else:
                    return newton_interpolacion(x_vals, y_vals, x_test)["valor"]

            y_graf = [eval_interpolacion(xv) for xv in x_graf]

            self.ax.clear()
            self.ax.plot(x_graf, y_graf, label="Interpolación", linewidth=2)
            self.ax.scatter(x_vals, y_vals, label="Datos", color="red", s=50)
            self.ax.scatter(x_eval, res["valor"], label=f"Evaluación en x={x_eval}", color="green", s=100, marker='x')

            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.ax.set_title(f"Interpolación {metodo}")
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)

            self.canvas.draw()

            self.lbl_resultado.config(text=f"Resultado: {res['valor']:.6f}")
            self.lbl_polinomio.config(text=f"Polinomio: {res['polinomio']}")

            self.text_proc.config(state="disabled")

        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error Detallado", error_msg)

    # =========================================================
    def _mostrar_procedimiento(self, metodo, res):

        t = self.text_proc

        t.insert("end", f"MÉTODO: Interpolación {metodo}\n\n")

        t.insert("end", f"X: {self.var_x.get()}\n")
        t.insert("end", f"Y: {self.var_y.get()}\n")
        t.insert("end", f"x eval: {self.var_eval.get()}\n\n")

        for h in res["historial"]:
            t.insert("end", h["detalle"] + "\n\n")

        t.insert("end", f"\nPOLINOMIO:\n{res['polinomio']}\n")
        t.insert("end", f"\nRESULTADO: {res['valor']}\n")

    # =========================================================
    def _exportar_pdf(self):

        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Primero calcula")
            return

        doc = SimpleDocTemplate(
            "interpolacion.pdf",
            pagesize=letter,
            leftMargin=60,
            rightMargin=60,
            topMargin=60,
            bottomMargin=60
        )

        estilos = getSampleStyleSheet()

        estilo = ParagraphStyle(
            "custom",
            parent=estilos["Normal"],
            alignment=TA_LEFT,
            fontSize=10,
            leading=14
        )

        contenido = []

        def add(x):
            contenido.append(Paragraph(x, estilo))
            contenido.append(Spacer(1, 8))

        add("<b>INTERPOLACIÓN NUMÉRICA</b>")
        add(f"Método: {self.var_met.get()}")
        add(f"X: {self.var_x.get()}")
        add(f"Y: {self.var_y.get()}")
        add(f"Evaluación: {self.var_eval.get()}")

        for h in self.ultimo_resultado["historial"]:
            add(h["detalle"])

        add(f"<b>Resultado:</b> {self.ultimo_resultado['valor']}")
        add(f"<b>Polinomio:</b> {self.ultimo_resultado['polinomio']}")

        doc.build(contenido)

        messagebox.showinfo("PDF", "Generado correctamente")