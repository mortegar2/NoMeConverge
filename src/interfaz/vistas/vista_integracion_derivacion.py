"""
VistaIntegracionDerivacion

Interfaz para el módulo de integración y derivación numérica.
Permite calcular derivadas por diferencias finitas y la integral mediante
trapecio y Simpson, mostrando el procedimiento y generando un reporte PDF.
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

from src.algoritmos.integracion_derivacion import diferencias_finitas, trapecio_compuesto, simpson_compuesto, derivada_en_punto
from src.utilidades.evaluador_funciones import EvaluadorFunciones


class VistaIntegracionDerivacion:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.ultimo_resultado = None
        self._crear_ui()

    def _format(self, value):
        try:
            return f"{float(value):.6f}"
        except Exception:
            return str(value)

    def _crear_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        control_frame = ttk.Labelframe(self.parent, text="Parámetros")
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(control_frame, text="f(x) =").grid(row=0, column=0, sticky="w")
        self.var_f = tk.StringVar(value="sin(x)")
        ttk.Entry(control_frame, textvariable=self.var_f).grid(row=0, column=1, sticky="ew")

        ttk.Label(control_frame, text="Método").grid(row=1, column=0, sticky="w")
        self.var_met = tk.StringVar(value="Diferencias finitas")
        combo_met = ttk.Combobox(
            control_frame,
            textvariable=self.var_met,
            values=["Diferencias finitas", "Trapecio", "Simpson"],
            state="readonly"
        )
        combo_met.grid(row=1, column=1, sticky="ew")
        combo_met.bind("<<ComboboxSelected>>", self._ajustar_campos)

        self.lbl_diff = ttk.Label(control_frame, text="Tipo de diferencia")
        self.lbl_diff.grid(row=2, column=0, sticky="w")
        self.var_diff = tk.StringVar(value="central")
        self.combo_diff = ttk.Combobox(
            control_frame,
            textvariable=self.var_diff,
            values=["adelante", "atrás", "central"],
            state="readonly"
        )
        self.combo_diff.grid(row=2, column=1, sticky="ew")
        self.combo_diff.bind("<<ComboboxSelected>>", self._ajustar_campos)

        self.lbl_x0 = ttk.Label(control_frame, text="a / x0")
        self.lbl_x0.grid(row=3, column=0, sticky="w")
        self.var_x0 = tk.StringVar(value="0")
        self.ent_x0 = ttk.Entry(control_frame, textvariable=self.var_x0)
        self.ent_x0.grid(row=3, column=1, sticky="ew")

        self.lbl_x1 = ttk.Label(control_frame, text="b / x1")
        self.lbl_x1.grid(row=4, column=0, sticky="w")
        self.var_x1 = tk.StringVar(value="3.1416")
        self.ent_x1 = ttk.Entry(control_frame, textvariable=self.var_x1)
        self.ent_x1.grid(row=4, column=1, sticky="ew")

        self.lbl_n = ttk.Label(control_frame, text="n (puntos/subintervalos)")
        self.lbl_n.grid(row=5, column=0, sticky="w")
        self.var_n = tk.StringVar(value="10")
        self.ent_n = ttk.Entry(control_frame, textvariable=self.var_n)
        self.ent_n.grid(row=5, column=1, sticky="ew")

        ttk.Label(control_frame, text="h (paso)").grid(row=6, column=0, sticky="w")
        self.var_h = tk.StringVar(value="0.001")
        self.ent_h = ttk.Entry(control_frame, textvariable=self.var_h)
        self.ent_h.grid(row=6, column=1, sticky="ew")

        frame_buttons = ttk.Frame(control_frame)
        frame_buttons.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(frame_buttons, text="Calcular", command=self._ejecutar).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="PDF", command=self._exportar_pdf).pack(side="left", padx=5)

        self.lbl_resultado = ttk.Label(control_frame, text="")
        self.lbl_resultado.grid(row=8, column=0, columnspan=2, pady=5)

        # =========================
        # GUIA DE USUARIO (panel superior derecho)
        # =========================
        guia = ttk.Labelframe(self.parent, text="Guía de uso")
        guia.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        texto_guia = (
            "DERIVACIÓN: f(x), x0 (punto), h (paso pequeño).\n"
            "- adelante: usa f(x0+h).\n"
            "- atrás: usa f(x0-h).\n"
            "- central: usa ambos.\n\n"
            "INTEGRACIÓN: f(x), a, b, n (subintervalos).\n"
            "- Trapecio: aproximación lineal.\n"
            "- Simpson: aproximación parabólica (n par).\n\n"
            "Reglas: h pequeño en derivación; n entero positivo; a < b."
        )

        self.lbl_guia = ttk.Label(guia, text=texto_guia, justify="left", wraplength=380)
        self.lbl_guia.pack(fill="both", expand=True, padx=6, pady=6)

        self._ajustar_campos(None)

        panel_proc = ttk.Labelframe(self.parent, text="Procedimiento Paso a Paso")
        panel_proc.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        panel_proc.grid_rowconfigure(0, weight=1)
        panel_proc.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(panel_proc)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.text_proc = tk.Text(panel_proc, wrap="word", font=("Courier", 9), yscrollcommand=scrollbar.set, padx=10, pady=10)
        self.text_proc.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.text_proc.yview)

        panel_graf = ttk.Labelframe(self.parent, text="Gráfica")
        panel_graf.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.fig = Figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_graf)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _ajustar_campos(self, event):
        metodo = self.var_met.get()
        if metodo == "Diferencias finitas":
            self.lbl_x0.config(text="x0")
            self.lbl_x1.config(text="b / x1")
            self.lbl_x0.grid()
            self.ent_x0.grid()
            self.lbl_x1.grid_remove()
            self.ent_x1.grid_remove()
            self.lbl_n.grid_remove()
            self.ent_n.grid_remove()
            self.ent_h.grid()
            self.lbl_diff.grid()
            self.combo_diff.grid()

            guia_texto = (
                "DERIVACIÓN NUMÉRICA CON DIFERENCIAS FINITAS:\n"
                "Ingrese f(x), x0 y el paso h.\n"
                "Seleccione el tipo de diferencia:\n"
                "  • adelante = f(x0+h)-f(x0) / h\n"
                "  • atrás = f(x0)-f(x0-h) / h\n"
                "  • central = (f(x0+h)-f(x0-h)) / (2h)\n\n"
                "Reglas:\n"
                "  • h debe ser pequeño y positivo.\n"
                "  • x0 es el punto donde aproximar la derivada.\n"
                "  • Solo se muestran valores con 6 decimales."
            )
        else:
            self.lbl_x0.config(text="a")
            self.lbl_x1.config(text="b")
            self.lbl_x0.grid()
            self.ent_x0.grid()
            self.lbl_x1.grid()
            self.ent_x1.grid()
            self.lbl_n.grid()
            self.ent_n.grid()
            self.ent_h.grid_remove()
            self.lbl_diff.grid_remove()
            self.combo_diff.grid_remove()

            guia_texto = (
                "INTEGRACIÓN NUMÉRICA:\n"
                "Ingrese f(x), los extremos a y b, y el número de subintervalos n.\n"
                "Trapecio usa regiones lineales.\n"
                "Simpson usa regiones parabólicas (n par).\n\n"
                "Reglas:\n"
                "  • a < b.\n"
                "  • n entero positivo.\n"
                "  • n par para Simpson.\n"
                "  • Los resultados usan 6 decimales."
            )

        self.lbl_guia.config(text=guia_texto)

    def _ejecutar(self):
        try:
            f = EvaluadorFunciones.crear_funcion_univariable(self.var_f.get())
            a = float(self.var_x0.get())
            b = float(self.var_x1.get())
            n = int(self.var_n.get())

            self.text_proc.config(state="normal")
            self.text_proc.delete("1.0", "end")

            metodo = self.var_met.get()
            if metodo == "Diferencias finitas":
                h = float(self.var_h.get())
                x0 = float(self.var_x0.get())
                submethod = self.var_diff.get()
                metodo_map = {"adelante": "forward", "atrás": "backward", "central": "central"}
                resultado = derivada_en_punto(f, x0=x0, h=h, method=metodo_map.get(submethod, "central"))
                self.ultimo_resultado = resultado
                self.lbl_resultado.config(text=f"Derivada aproximada en x0 = {self._format(x0)}: {self._format(resultado['valor'])}")
                self._mostrar_diferencias(resultado)
                self._graficar_diferencias(resultado)
            elif metodo == "Trapecio":
                resultado = trapecio_compuesto(f, a, b, n=n)
                self.ultimo_resultado = resultado
                self.lbl_resultado.config(text=f"Integral aproximada = {resultado['valor']:.6g}")
                self._mostrar_integracion(resultado)
                self._graficar_integracion(resultado)
            else:
                resultado = simpson_compuesto(f, a, b, n=n)
                self.ultimo_resultado = resultado
                self.lbl_resultado.config(text=f"Integral aproximada = {resultado['valor']:.6g}")
                self._mostrar_integracion(resultado)
                self._graficar_integracion(resultado)

            self.text_proc.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _mostrar_diferencias(self, resultado):
        # Mostrar detalle para derivada en punto o diferencias múltiples
        if resultado.get("metodo") == "Derivación en punto":
            self.text_proc.insert("end", f"MÉTODO: Derivación en punto ({resultado['submetodo']})\n\n")
            # Datos de entrada
            self.text_proc.insert("end", "Datos de entrada:\n")
            self.text_proc.insert("end", f"  Función: {self.var_f.get()}\n")
            self.text_proc.insert("end", f"  Punto x0: {self._format(resultado['x0'])}\n")
            self.text_proc.insert("end", f"  Paso h: {self._format(resultado['h'])}\n\n")

            # Fórmula
            self.text_proc.insert("end", f"Fórmula usada:\n  {resultado.get('formula', '')}\n\n")

            # Evaluaciones
            self.text_proc.insert("end", "Evaluaciones:\n")
            for ev in resultado.get('evaluaciones', []):
                self.text_proc.insert("end", f"  {ev['expr']} = {self._format(ev['valor'])}\n")
            self.text_proc.insert("end", "\n")

            # Sustitución y resultado
            self.text_proc.insert("end", f"Sustitución:\n  {resultado.get('sustitucion', '')}\n\n")
            self.text_proc.insert("end", f"Resultado:\n  f'({self._format(resultado['x0'])}) ≈ {self._format(resultado['valor'])}\n\n")

            # Tabla de evaluaciones
            self.text_proc.insert("end", "Tabla de evaluaciones:\n")
            self.text_proc.insert("end", "  |   x   |   f(x)   |\n")
            self.text_proc.insert("end", "  |-------|---------|\n")
            for fila in resultado.get('tabla', []):
                self.text_proc.insert("end", f"  | {self._format(fila['x'])} | {self._format(fila['f(x)'])} |\n")
            self.text_proc.insert("end", "\n")

            # Historial (detalles)
            for paso in resultado.get("historial", []):
                self.text_proc.insert("end", paso.get("detalle", "") + "\n")
        else:
            self.text_proc.insert("end", f"MÉTODO: Diferencias finitas ({resultado.get('submetodo', '')})\n\n")
            for paso in resultado.get("resultados", []):
                self.text_proc.insert("end", paso.get("detalle", "") + "\n")

    def _mostrar_integracion(self, resultado):
        metodo = resultado['metodo']
        self.text_proc.insert("end", f"MÉTODO: {metodo}\n\n")
        
        # Datos de entrada
        self.text_proc.insert("end", "Datos de entrada:\n")
        self.text_proc.insert("end", f"  Función: {self.var_f.get()}\n")
        self.text_proc.insert("end", f"  Intervalo: [{self._format(resultado['a'])}, {self._format(resultado['b'])}]\n")
        self.text_proc.insert("end", f"  Subintervalos n: {resultado['n']}\n")
        self.text_proc.insert("end", f"  Paso h = {resultado['h']}\n\n")

        # Fórmula
        self.text_proc.insert("end", f"Fórmula\n\n  {resultado.get('formula', '')}\n\n")

        # Tabla
        self.text_proc.insert("end", "Tabla de evaluaciones:\n")
        if "peso" in resultado['tabla'][0]:
            # Simpson
            self.text_proc.insert("end", "  | i | x | f(x) | peso |\n")
            self.text_proc.insert("end", "  |---|---|------|------|\n")
            for fila in resultado['tabla']:
                self.text_proc.insert("end", f"  | {fila['i']} | {fila['x']} | {fila['f(x)']} | {fila['peso']} |\n")
        else:
            # Trapecio
            self.text_proc.insert("end", "  | i | x | f(x) |\n")
            self.text_proc.insert("end", "  |---|---|------|\n")
            for fila in resultado['tabla']:
                self.text_proc.insert("end", f"  | {fila['i']} | {fila['x']} | {fila['f(x)']} |\n")
        self.text_proc.insert("end", "\n")

        # Sustitución
        self.text_proc.insert("end", f"Sustitución\n\n  {resultado.get('sustitucion', '')}\n")
        if "Trapecio" in metodo:
            self.text_proc.insert("end", f"\n  Integral ≈ (h/2) * S = {self._format(resultado['valor'])}\n\n")
        else:
            self.text_proc.insert("end", f"\n  Integral ≈ (h/3) * S = {self._format(resultado['valor'])}\n\n")

        # Resultado
        self.text_proc.insert("end", f"Resultado\n\n  {self._format(resultado['valor'])}\n\n")

    def _graficar_diferencias(self, resultado):
        f = EvaluadorFunciones.crear_funcion_univariable(self.var_f.get())
        self.ax.clear()
        if resultado.get("metodo") == "Derivación en punto":
            x0 = resultado["x0"]
            h = resultado["h"]
            deriv = resultado["valor"]
            # dominio for plot
            span = max(1.0, abs(h * 10))
            x_line = np.linspace(x0 - span, x0 + span, 400)
            y_line = np.array([f(x) for x in x_line])
            self.ax.plot(x_line, y_line, color="#1f77b4", label="f(x)")
            # mark x0
            self.ax.scatter([x0], [f(x0)], color="#d62728", s=80, label="x0")
            # approximate tangent line
            y_tan = f(x0) + deriv * (x_line - x0)
            self.ax.plot(x_line, y_tan, color="#2ca02c", linestyle="--", label="Tangente approx")
            self.ax.set_title("Derivada en punto (aprox)")
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("f(x)")
            self.ax.grid(True, linestyle="--", alpha=0.6)
            self.ax.legend()
            self.canvas.draw()
        else:
            a = resultado["a"]
            b = resultado["b"]
            x_line = np.linspace(a, b, 400)
            y_line = np.array([f(x) for x in x_line])
            self.ax.plot(x_line, y_line, color="#1f77b4", label="f(x)")
            # shade area
            self.ax.fill_between(x_line, y_line, where=(x_line >= a) & (x_line <= b), color="#c6dbef", alpha=0.5)
            # partition points
            xs = [p["x"] for p in resultado["resultados"]]
            ys = [p["f(x)"] for p in resultado["resultados"]]
            self.ax.scatter(xs, ys, color="#d62728", label="xi")
            self.ax.set_title(resultado["metodo"])
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("f(x)")
            self.ax.grid(True, linestyle="--", alpha=0.6)
            self.ax.legend()
            self.canvas.draw()

    def _graficar_integracion(self, resultado):
        from scipy.interpolate import lagrange
        
        a = resultado["a"]
        b = resultado["b"]
        n = resultado["n"]
        metodo = resultado['metodo']
        
        f = EvaluadorFunciones.crear_funcion_univariable(self.var_f.get())
        
        # Curva original con alta resolución
        x_line = np.linspace(a, b, 400)
        y_line = np.array([f(x) for x in x_line])

        # Puntos de evaluación
        xs_eval = np.linspace(a, b, n + 1).tolist()
        ys_eval = [f(x) for x in xs_eval]

        self.ax.clear()

        if "Trapecio" in metodo:
            # ===== TRAPECIO =====
            # 1. Curva original en AZUL (línea punteada, de referencia)
            self.ax.plot(x_line, y_line, color="#1f77b4", linewidth=2, linestyle="-", 
                        label="Curva original", zorder=2)
            
            # 2. Aproximación con trapecios: líneas rectas en NARANJA
            for i in range(len(xs_eval) - 1):
                x_trap = [xs_eval[i], xs_eval[i + 1]]
                y_trap = [ys_eval[i], ys_eval[i + 1]]
                self.ax.plot(x_trap, y_trap, color="#ff7f0e", linewidth=2.5, zorder=3)
            
            # 3. Área sombreada de trapecios en NARANJA TRANSPARENTE
            for i in range(len(xs_eval) - 1):
                x_trap = [xs_eval[i], xs_eval[i + 1], xs_eval[i + 1], xs_eval[i]]
                y_trap = [ys_eval[i], ys_eval[i + 1], 0, 0]
                self.ax.fill(x_trap, y_trap, color="#ff7f0e", alpha=0.25, edgecolor="none", zorder=1)
            
            # 4. Puntos en ROJO
            self.ax.scatter(xs_eval, ys_eval, color="#d62728", s=80, zorder=5, 
                           label="Puntos de evaluación", edgecolors="darkred", linewidth=1)
            
            self.ax.set_title("Método del Trapecio Compuesto\n(aproximación con segmentos rectos)", 
                             fontsize=12, fontweight="bold")
            
        else:
            # ===== SIMPSON =====
            # 1. Curva original en AZUL
            self.ax.plot(x_line, y_line, color="#1f77b4", linewidth=2, linestyle="-", 
                        label="Curva original", zorder=2)
            
            # 2. Aproximación con Simpson: curvas parabólicas en NARANJA
            # Crear interpolación parabólica por cada par de subintervalos
            h = (b - a) / n
            for i in range(0, len(xs_eval) - 2, 2):
                # Tomar 3 puntos consecutivos para una parábola
                x_parab = xs_eval[i:i+3]
                y_parab = ys_eval[i:i+3]
                
                # Crear polinomio de Lagrange de grado 2 (parábola)
                if len(x_parab) == 3:
                    try:
                        poly = lagrange(x_parab, y_parab)
                        x_smooth = np.linspace(x_parab[0], x_parab[2], 50)
                        y_smooth = poly(x_smooth)
                        self.ax.plot(x_smooth, y_smooth, color="#ff7f0e", linewidth=2.5, zorder=3)
                        
                        # Sombrear área bajo la parábola
                        self.ax.fill_between(x_smooth, 0, y_smooth, color="#ff7f0e", alpha=0.25, zorder=1)
                    except Exception:
                        pass
            
            # 3. Puntos en ROJO
            self.ax.scatter(xs_eval, ys_eval, color="#d62728", s=80, zorder=5, 
                           label="Puntos de evaluación", edgecolors="darkred", linewidth=1)
            
            self.ax.set_title("Método de Simpson Compuesto\n(aproximación con curvas parabólicas)", 
                             fontsize=12, fontweight="bold")

        self.ax.axhline(y=0, color="black", linewidth=0.8, linestyle="-", alpha=0.3)
        self.ax.set_xlabel("x", fontsize=11)
        self.ax.set_ylabel("f(x)", fontsize=11)
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.ax.legend(loc="best", fontsize=10)
        self.ax.set_xlim(a - 0.05 * (b - a), b + 0.05 * (b - a))
        self.canvas.draw()

    def _exportar_pdf(self):
        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Primero calcula")
            return

        nombre_archivo = "integracion_derivacion.pdf"
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
        contenido.append(Paragraph("INTEGRACIÓN Y DERIVACIÓN NUMÉRICA", estilo_titulo))
        contenido.append(Paragraph(f"Ejercicio: {self.var_met.get()}", estilo_subtitulo))

        metodo = self.var_met.get()
        datos = [["Función:", self.var_f.get()], ["Método:", metodo]]
        if metodo == "Diferencias finitas":
            datos.extend([
                ["Punto x0:", self._format(self.var_x0.get())],
                ["Paso h:", self._format(self.var_h.get())]
            ])
        else:
            datos.extend([
                ["Intervalo:", f"[{self._format(self.var_x0.get())}, {self._format(self.var_x1.get())}]"],
                ["Subintervalos n:", str(self.var_n.get())]
            ])

        tabla_datos = Table(datos, colWidths=[150, 320])
        tabla_datos.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ]))

        contenido.append(tabla_datos)
        contenido.append(Spacer(1, 12))

        guia_texto = (
            "Guía de uso:\n"
            f"Método: {metodo}.\n"
        )
        if metodo == "Diferencias finitas":
            guia_texto += (
                "Ingrese f(x), x0 y h.\n"
                "adelante usa f(x0+h) - f(x0).\n"
                "atrás usa f(x0) - f(x0-h).\n"
                "central usa f(x0+h) - f(x0-h) sobre 2h.\n"
                "Los resultados se muestran con 6 decimales."
            )
        else:
            guia_texto += (
                "Ingrese f(x), a, b y n.\n"
                "Trapecio aplica regiones lineales.\n"
                "Simpson aplica regiones parabólicas.\n"
                "n debe ser entero positivo y par para Simpson.\n"
                "Los resultados se muestran con 6 decimales."
            )

        contenido.append(Paragraph(guia_texto.replace("\n", "<br/>"), estilo_normal))
        contenido.append(Spacer(1, 20))

        buffer = BytesIO()
        self.fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        buffer.seek(0)
        imagen = Image(buffer, width=440, height=320)
        imagen.hAlign = "CENTER"
        contenido.append(imagen)
        contenido.append(PageBreak())

        contenido.append(Paragraph("Desarrollo del método", estilo_titulo))
        contenido.append(Spacer(1, 10))

        for paso in self.ultimo_resultado["historial"]:
            contenido.append(Paragraph(f"<b>Iteración {paso['iter']}</b>", estilo_normal))
            contenido.append(Paragraph(paso["detalle"].replace("\n", "<br/>"), estilo_normal))
            contenido.append(Spacer(1, 8))

        contenido.append(PageBreak())
        contenido.append(Paragraph("Tabla de resultados", estilo_titulo))
        contenido.append(Spacer(1, 8))

        headers = list(self.ultimo_resultado["resultados"][0].keys())
        data = [headers]
        for fila in self.ultimo_resultado["resultados"]:
            data.append([str(fila[col]) for col in headers])

        tabla_resultados = Table(data, colWidths=[100] * len(headers))
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
