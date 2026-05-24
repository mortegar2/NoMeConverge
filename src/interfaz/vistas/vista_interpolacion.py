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
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors

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

        ttk.Label(ctrl, text="Evaluar x = (opcional)").grid(row=2, column=0, sticky="w")
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
        help_frame = ttk.Labelframe(self.parent, text="Guía de funciones")
        help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        tree = ttk.Treeview(help_frame, columns=("c1", "c2"), show="headings")
        tree.heading("c1", text="Concepto")
        tree.heading("c2", text="Ejemplo")

        for d in [
            ("X", "1,2,3"),
            ("Y", "2,4,9"),
            ("x eval (opcional)", "2.5 o dejar vacío"),
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

    def _coefs_polinomio(self, x_vals, y_vals):
        """Obtiene coeficientes polinomiales para interpolación."""
        return np.polyfit(x_vals, y_vals, len(x_vals) - 1)

    # =========================================================
    def _ejecutar(self):

        try:
            x_raw = self.var_x.get().strip()
            y_raw = self.var_y.get().strip()

            if not x_raw or not y_raw:
                raise ValueError("Debe ingresar valores para X y Y.")

            x_vals = self._parse(x_raw)
            y_vals = self._parse(y_raw)
            
            # Hacer x_eval opcional
            var_eval_str = self.var_eval.get().strip()
            x_eval = float(var_eval_str) if var_eval_str else None

            if len(x_vals) != len(y_vals):
                raise ValueError("X e Y deben tener la misma longitud.")

            if len(set(x_vals)) != len(x_vals):
                raise ValueError("Los valores de X deben ser únicos; no se permiten repeticiones.")

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

            coefs = self._coefs_polinomio(x_vals, y_vals)
            polinomio_evaluador = np.poly1d(coefs)
            y_graf = polinomio_evaluador(x_graf)

            self.ax.clear()
            self.ax.plot(x_graf, y_graf, label="Interpolación", linewidth=2)
            self.ax.scatter(x_vals, y_vals, label="Datos", color="red", s=50)
            
            # Mostrar punto de evaluación solo si se proporciona
            if x_eval is not None:
                self.ax.scatter(x_eval, res["valor"], label=f"Evaluación en x={x_eval}", color="green", s=100, marker='x')

            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.ax.set_title(f"Interpolación {metodo}")
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)

            self.canvas.draw()

            # Mostrar resultado solo si se evaluó
            if res["valor"] is not None:
                self.lbl_resultado.config(text=f"Resultado: {res['valor']:.6f}")
            else:
                self.lbl_resultado.config(text="Polinomio construido sin evaluación")
            
            self.lbl_polinomio.config(text=f"Polinomio: {res['polinomio']}")

            self.text_proc.config(state="disabled")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
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
        
        # Mostrar x eval solo si se proporcionó
        if res["valor_evaluado"] is not None:
            t.insert("end", f"x eval: {res['valor_evaluado']}\n\n")
        else:
            t.insert("end", f"x eval: (no especificado - construyendo solo el polinomio)\n\n")

        # Mostrar historial solo si hay pasos (cuando se evaluó)
        if res["historial"]:
            for h in res["historial"]:
                t.insert("end", h["detalle"] + "\n\n")

        t.insert("end", f"\nPOLINOMIO:\n{res['polinomio']}\n")
        
        # Mostrar resultado solo si se evaluó
        if res["valor"] is not None:
            t.insert("end", f"\nRESULTADO: {res['valor']}\n")
        else:
            t.insert("end", f"\n(Polinomio construido. Para evaluar, ingrese un valor en 'Evaluar x')\n")

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

        puntos_x = self._parse(self.var_x.get())
        puntos_y = self._parse(self.var_y.get())

        contenido = []
        contenido.append(Paragraph("INTERPOLACIÓN NUMÉRICA", estilo_titulo))
        contenido.append(Paragraph(f"Ejercicio: Interpolación con {self.var_met.get()}", estilo_subtitulo))

        num_iteraciones = len(self.ultimo_resultado["historial"]) if self.ultimo_resultado["historial"] else 0
        
        meta = [
            ["Método:", self.var_met.get()],
            ["Iteraciones utilizadas:", str(num_iteraciones)],
            ["Punto evaluado:", f"x = {self.ultimo_resultado['valor_evaluado']}" if self.ultimo_resultado['valor_evaluado'] is not None else "No especificado"],
            ["Resultado de la evaluación:", f"{self.ultimo_resultado['valor']:.16g}" if self.ultimo_resultado['valor'] is not None else "No evaluado"],
            ["Polinomio interpolante:", self.ultimo_resultado['polinomio']]
        ]

        tabla_meta = Table(meta, colWidths=[150, 300])
        tabla_meta.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black)
        ]))

        contenido.append(tabla_meta)
        contenido.append(Spacer(1, 20))

        contenido.append(Paragraph("Puntos originales", estilo_subtitulo))
        puntos = [[Paragraph("<b>x</b>", estilo_normal), Paragraph("<b>y</b>", estilo_normal)]]
        for x_val, y_val in zip(puntos_x, puntos_y):
            puntos.append([f"{x_val:.6g}", f"{y_val:.6g}"])

        tabla_puntos = Table(puntos, colWidths=[150, 150])
        tabla_puntos.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5597")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))

        contenido.append(tabla_puntos)
        contenido.append(PageBreak())

        buffer = BytesIO()
        self.fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        buffer.seek(0)
        imagen = Image(buffer, width=440, height=320)
        imagen.hAlign = "CENTER"

        contenido.append(Paragraph("Gráfica de interpolación", estilo_titulo))
        contenido.append(Spacer(1, 12))
        contenido.append(imagen)
        contenido.append(PageBreak())

        contenido.append(Paragraph("Desarrollo del método", estilo_titulo))
        contenido.append(Spacer(1, 10))

        if self.ultimo_resultado["historial"]:
            for paso in self.ultimo_resultado["historial"]:
                contenido.append(Paragraph(f"<b>Iteración {paso['iter']}:</b>", estilo_normal))
                contenido.append(Paragraph(paso["detalle"].replace("\n", "<br/>"), estilo_normal))
                contenido.append(Spacer(1, 12))
        else:
            contenido.append(Paragraph("No hay desarrollo del método disponible porque no se proporcionó un punto de evaluación.", estilo_normal))

        doc.build(contenido)

        messagebox.showinfo("PDF", "Generado correctamente")