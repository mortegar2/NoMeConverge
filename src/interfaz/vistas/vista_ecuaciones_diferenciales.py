"""VistaEcuacionesDiferenciales

Interfaz gráfica para resolver ecuaciones diferenciales ordinarias por
Euler y Runge-Kutta de cuarto orden.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

from src.algoritmos.ecuaciones_diferenciales import euler, runge_kutta_4
from src.utilidades.evaluador_funciones import EvaluadorFunciones
from src.utilidades.excepciones import ParametrosInvalidosError


class VistaEcuacionesDiferenciales:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.ultimo_resultado = None
        self._crear_ui()

    def _crear_ui(self):
        self.parent.grid_rowconfigure(0, weight=2)
        self.parent.grid_rowconfigure(1, weight=3)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        ctrl = ttk.Labelframe(self.parent, text="Parámetros")
        ctrl.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.var_f = tk.StringVar(value="t + y")
        self.var_met = tk.StringVar(value="Euler")
        self.var_t0 = tk.StringVar(value="0")
        self.var_y0 = tk.StringVar(value="1")
        self.var_tf = tk.StringVar(value="2")
        self.var_n = tk.StringVar(value="10")

        ttk.Label(ctrl, text="f(t, y) =").grid(row=0, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_f).grid(row=0, column=1, sticky="ew")

        ttk.Label(ctrl, text="Método").grid(row=1, column=0, sticky="w")
        combo = ttk.Combobox(
            ctrl,
            textvariable=self.var_met,
            values=["Euler", "Runge-Kutta 4"],
            state="readonly"
        )
        combo.grid(row=1, column=1, sticky="ew")

        ttk.Label(ctrl, text="t0").grid(row=2, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_t0).grid(row=2, column=1, sticky="ew")

        ttk.Label(ctrl, text="y0").grid(row=3, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_y0).grid(row=3, column=1, sticky="ew")

        ttk.Label(ctrl, text="tf").grid(row=4, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_tf).grid(row=4, column=1, sticky="ew")

        ttk.Label(ctrl, text="n pasos").grid(row=5, column=0, sticky="w")
        ttk.Entry(ctrl, textvariable=self.var_n).grid(row=5, column=1, sticky="ew")

        frame_btn = ttk.Frame(ctrl)
        frame_btn.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(frame_btn, text="Calcular", command=self._ejecutar).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="PDF", command=self._exportar_pdf).pack(side="left", padx=5)

        self.lbl_resultado = ttk.Label(ctrl, text="")
        self.lbl_resultado.grid(row=7, column=0, columnspan=2, pady=5)

        guia = ttk.Labelframe(self.parent, text="Guía de uso")
        guia.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        texto_guia = (
            "ECUACIONES DIFERENCIALES:\n"
            "Ingrese f(t,y), condición inicial y intervalo.\n"
            "Euler usa aproximación paso a paso.\n"
            "Runge-Kutta 4 usa cuatro evaluaciones por paso.\n"
            "\n"
            "Ejemplo: f(t,y) = t + y\n"
            "t0 = 0, y0 = 1, tf = 2, n = 10\n"
            "\n"
            "Reglas:\n"
            "  • tf > t0.\n"
            "  • n entero positivo.\n"
            "  • f debe usar t y y como variables.\n"
        )

        self.lbl_guia = ttk.Label(guia, text=texto_guia, justify="left", wraplength=380)
        self.lbl_guia.pack(fill="both", expand=True, padx=6, pady=6)

        frame_proc = ttk.Labelframe(self.parent, text="Procedimiento Paso a Paso")
        frame_proc.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_proc.grid_rowconfigure(0, weight=1)
        frame_proc.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame_proc)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.text_proc = tk.Text(frame_proc, wrap="word", font=("Courier", 9), yscrollcommand=scrollbar.set, padx=10, pady=10)
        self.text_proc.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.text_proc.yview)

        frame_graf = ttk.Labelframe(self.parent, text="Gráfica")
        frame_graf.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.fig = Figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_graf)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _crear_funcion_bivariable(self, expresion: str):
        expresion = EvaluadorFunciones._normalizar_expresion(expresion)
        namespace = EvaluadorFunciones.NAMESPACE_SEGURO.copy()

        try:
            eval(expresion, {"__builtins__": {}}, {**namespace, "t": 1.0, "y": 1.0})
        except Exception as e:
            raise ValueError(f"Expresión inválida: {e}")

        def f(t_val: float, y_val: float) -> float:
            try:
                return eval(expresion, {"__builtins__": {}}, {**namespace, "t": t_val, "y": y_val})
            except Exception:
                return float("nan")

        return f

    def _ejecutar(self):
        try:
            f = self._crear_funcion_bivariable(self.var_f.get())
            t0 = float(self.var_t0.get())
            y0 = float(self.var_y0.get())
            tf = float(self.var_tf.get())
            n = int(self.var_n.get())
            metodo = self.var_met.get()

            self.text_proc.config(state="normal")
            self.text_proc.delete("1.0", "end")

            if metodo == "Euler":
                resultado = euler(f, t0, y0, tf, n)
            else:
                resultado = runge_kutta_4(f, t0, y0, tf, n)

            self.ultimo_resultado = resultado
            self.lbl_resultado.config(text=f"y({tf:.6f}) ≈ {resultado['valor']:.6g}")

            self._mostrar_procedimiento(resultado)
            self._graficar(resultado)
            self.text_proc.config(state="disabled")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except ParametrosInvalidosError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error Detallado", error_msg)

    def _mostrar_procedimiento(self, resultado):
        self.text_proc.insert("end", f"MÉTODO: {resultado['metodo']}\n\n")
        self.text_proc.insert("end", f"f(t,y) = {self.var_f.get()}\n")
        self.text_proc.insert("end", f"t0 = {resultado['t0']}, y0 = {resultado['y0']}\n")
        self.text_proc.insert("end", f"tf = {resultado['tf']}, n = {resultado['n']}, h = {resultado['h']}\n\n")

        for paso in resultado["historial"]:
            self.text_proc.insert("end", paso["detalle"] + "\n")

        self.text_proc.insert("end", f"RESULTADO FINAL: y({resultado['tf']}) ≈ {resultado['valor']}\n")

    def _graficar(self, resultado):
        ts = np.array(resultado["ts"])
        ys = np.array(resultado["ys"])

        self.ax.clear()
        self.ax.set_facecolor("#fafafa")
        self.ax.plot(ts, ys, color="#1f77b4", linewidth=2, label="Solución numérica")

        if resultado["metodo"] == "Euler":
            self.ax.step(ts, ys, where="post", color="#ff7f0e", linewidth=2.5, label="Euler (paso a paso)")
        else:
            self.ax.plot(ts, ys, color="#ff7f0e", linewidth=2.5, linestyle="--", label="RK4")

        self.ax.scatter(ts, ys, color="#d62728", s=60, zorder=5, label="Puntos")
        self.ax.axhline(0, color="black", linewidth=1, alpha=0.6)
        self.ax.axvline(0, color="black", linewidth=1, alpha=0.6)
        self.ax.set_xlabel("t")
        self.ax.set_ylabel("y")
        self.ax.set_title(f"{resultado['metodo']} - Solución de EDO")
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.legend(loc="best", fontsize=9)
        self.canvas.draw()

    def _exportar_pdf(self):
        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Primero calcula")
            return

        nombre_archivo = "ecuaciones_diferenciales.pdf"
        doc = SimpleDocTemplate(
            nombre_archivo,
            pagesize=letter,
            leftMargin=60,
            rightMargin=60,
            topMargin=60,
            bottomMargin=60
        )

        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle(
            "titulo",
            parent=estilos["Heading1"],
            alignment=TA_CENTER,
            fontSize=26,
            leading=32,
            spaceAfter=18,
            spaceBefore=12
        )
        estilo_subtitulo = ParagraphStyle(
            "subtitulo",
            parent=estilos["Heading2"],
            alignment=TA_CENTER,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2f5597"),
            spaceAfter=12
        )
        estilo_normal = ParagraphStyle(
            "normal",
            parent=estilos["BodyText"],
            alignment=TA_LEFT,
            fontSize=11,
            leading=16,
            spaceAfter=8
        )

        contenido = []
        contenido.append(Paragraph("ECUACIONES DIFERENCIALES", estilo_titulo))
        contenido.append(Paragraph(f"Ejercicio: {self.var_met.get()}", estilo_subtitulo))

        datos = [
            ["Función:", self.var_f.get()],
            ["Método:", self.var_met.get()],
            ["t0:", self.var_t0.get()],
            ["y0:", self.var_y0.get()],
            ["tf:", self.var_tf.get()],
            ["n:", self.var_n.get()],
            ["Resultado:", f"y({self.var_tf.get()}) ≈ {self.ultimo_resultado['valor']:.6g}"]
        ]

        tabla_datos = Table(datos, colWidths=[150, 320])
        tabla_datos.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ]))

        contenido.append(tabla_datos)
        contenido.append(Spacer(1, 12))

        texto = (
            f"Método: {self.var_met.get()}.\n"
            f"Se integra la EDO f(t,y) = {self.var_f.get()}.\n"
            "Se presenta el procedimiento paso a paso y la gráfica de la solución.\n"
        )
        contenido.append(Paragraph(texto.replace("\n", "<br/>"), estilo_normal))
        contenido.append(Spacer(1, 12))

        buffer = BytesIO()
        self.fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        buffer.seek(0)
        imagen = Image(buffer, width=440, height=300)
        imagen.hAlign = "CENTER"
        contenido.append(imagen)
        contenido.append(PageBreak())

        contenido.append(Paragraph("Procedimiento paso a paso", estilo_titulo))
        contenido.append(Spacer(1, 10))
        for paso in self.ultimo_resultado["historial"]:
            contenido.append(Paragraph(paso["detalle"].replace("\n", "<br/>"), estilo_normal))
            contenido.append(Spacer(1, 6))

        contenido.append(PageBreak())
        contenido.append(Paragraph("Tabla de resultados", estilo_titulo))
        contenido.append(Spacer(1, 10))

        headers = ["i", "t", "y", "f(t,y)"]
        if self.ultimo_resultado["metodo"] == "Runge-Kutta 4":
            headers = ["i", "t", "y", "k1", "k2", "k3", "k4", "y_next"]
        else:
            headers = ["i", "t", "y", "f(t,y)", "y_next"]

        filas = [headers]
        for fila in self.ultimo_resultado["tabla"]:
            filas.append([str(fila.get(col, "")) for col in headers])

        tabla_resultados = Table(filas, colWidths=[70] * len(headers))
        tabla_resultados.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5597")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        contenido.append(tabla_resultados)
        doc.build(contenido)
        messagebox.showinfo("PDF", "PDF generado correctamente")
