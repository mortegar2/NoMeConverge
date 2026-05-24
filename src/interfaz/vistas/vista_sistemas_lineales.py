"""
VistaSistemasLineales

Interfaz gráfica para resolver sistemas lineales utilizando Gauss-Seidel y LU.
Incluye procedimiento paso a paso y exportación de resultados a PDF.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

from src.algoritmos.sistemas_lineales import gauss_seidel, lu_factorization


class VistaSistemasLineales:

    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.ultimo_resultado = None
        self._crear_ui()

    def _crear_ui(self):
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=3)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        ctrl = ttk.Labelframe(self.parent, text="Parámetros")
        ctrl.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(ctrl, text="Matriz A:").grid(row=0, column=0, sticky="w")
        self.txt_a = tk.Text(ctrl, width=30, height=8, wrap="none")
        self.txt_a.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        self.txt_a.insert("1.0", "4 1 2\n3 5 1\n1 1 3")

        ttk.Label(ctrl, text="Vector b:").grid(row=2, column=0, sticky="w")
        self.var_b = tk.StringVar(value="4, 7, 3")
        ttk.Entry(ctrl, textvariable=self.var_b).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(ctrl, text="Método").grid(row=3, column=0, sticky="w")
        self.var_met = tk.StringVar(value="Gauss-Seidel")
        combo = ttk.Combobox(ctrl, textvariable=self.var_met, values=["Gauss-Seidel", "LU"], state="readonly")
        combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        combo.bind("<<ComboboxSelected>>", self._ajustar_campos)

        self.var_x0 = tk.StringVar(value="0, 0, 0")
        self.var_tol = tk.StringVar(value="1e-6")
        self.var_max = tk.StringVar(value="50")

        self.lbl_x0 = ttk.Label(ctrl, text="x0 inicial:")
        self.ent_x0 = ttk.Entry(ctrl, textvariable=self.var_x0)
        self.lbl_tol = ttk.Label(ctrl, text="Tolerancia")
        self.ent_tol = ttk.Entry(ctrl, textvariable=self.var_tol)
        self.lbl_max = ttk.Label(ctrl, text="Max Iter")
        self.ent_max = ttk.Entry(ctrl, textvariable=self.var_max)

        self.lbl_x0.grid(row=4, column=0, sticky="w")
        self.ent_x0.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_tol.grid(row=5, column=0, sticky="w")
        self.ent_tol.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_max.grid(row=6, column=0, sticky="w")
        self.ent_max.grid(row=6, column=1, sticky="ew", padx=5, pady=2)

        frame_btn = ttk.Frame(ctrl)
        frame_btn.grid(row=7, column=0, columnspan=2, pady=10)

        ttk.Button(frame_btn, text="Calcular", command=self._ejecutar).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="PDF", command=self._exportar_pdf).pack(side="left", padx=5)

        self.lbl_resultado = ttk.Label(ctrl, text="")
        self.lbl_resultado.grid(row=8, column=0, columnspan=2, pady=5)

        help_frame = ttk.Labelframe(self.parent, text="Guía de uso")
        help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        tree = ttk.Treeview(help_frame, columns=("descripcion",), show="headings", height=5)
        tree.heading("descripcion", text="Ejemplo")
        tree.insert("", "end", values=("A puede escribirse como filas separadas por salto de línea",))
        tree.insert("", "end", values=("b puede ingresarse como 4, 7, 3",))
        tree.insert("", "end", values=("Gauss-Seidel usa x0, tol y max iter",))
        tree.insert("", "end", values=("LU resuelve Ax = b con factorización",))
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        frame_proc = ttk.Labelframe(self.parent, text="Procedimiento Paso a Paso")
        frame_proc.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        frame_proc.grid_rowconfigure(0, weight=1)
        frame_proc.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame_proc)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.text_proc = tk.Text(frame_proc, wrap="word", font=("Courier", 9), yscrollcommand=scrollbar.set, padx=10, pady=10)
        self.text_proc.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.text_proc.yview)

        self._ajustar_campos(None)

    def _parse_matrix(self, text):
        filas = [fila.strip() for fila in text.strip().splitlines() if fila.strip()]
        A = []
        for fila in filas:
            valores = [float(valor) for valor in fila.replace(",", " ").split()]
            A.append(valores)

        if len(A) == 0 or any(len(fila) != len(A) for fila in A):
            raise ValueError("La matriz A debe ser cuadrada y tener la misma cantidad de elementos por fila.")

        return A

    def _parse_vector(self, text):
        valores = [valor for valor in text.replace(",", " ").split() if valor]
        if not valores:
            raise ValueError("El vector no puede estar vacío.")
        return [float(valor) for valor in valores]

    def _ajustar_campos(self, event):
        metodo = self.var_met.get()

        if metodo == "Gauss-Seidel":
            self.lbl_x0.grid()
            self.ent_x0.grid()
            self.lbl_tol.grid()
            self.ent_tol.grid()
            self.lbl_max.grid()
            self.ent_max.grid()
        else:
            self.lbl_x0.grid_remove()
            self.ent_x0.grid_remove()
            self.lbl_tol.grid_remove()
            self.ent_tol.grid_remove()
            self.lbl_max.grid_remove()
            self.ent_max.grid_remove()

    def _ejecutar(self):
        try:
            A = self._parse_matrix(self.txt_a.get("1.0", "end"))
            b = self._parse_vector(self.var_b.get())
            metodo = self.var_met.get()

            self.text_proc.config(state="normal")
            self.text_proc.delete("1.0", "end")

            if metodo == "Gauss-Seidel":
                x0_text = self.var_x0.get().strip()
                x0 = self._parse_vector(x0_text) if x0_text else None
                tol = float(self.var_tol.get())
                max_iter = int(self.var_max.get())
                resultado = gauss_seidel(A, b, x0=x0, tol=tol, max_iter=max_iter)
                self.ultimo_resultado = resultado
                self.lbl_resultado.config(text=f"Solución: {resultado['solucion']} | Iteraciones: {resultado['iteraciones']}")
            else:
                resultado = lu_factorization(A, b)
                self.ultimo_resultado = resultado
                self.lbl_resultado.config(text=f"Solución: {resultado['x']}")

            self._mostrar_procedimiento(metodo, self.ultimo_resultado)
            self.text_proc.config(state="disabled")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error Detallado", error_msg)

    def _format_matrix(self, matrix):
        return "\n".join(["  " + ", ".join(f"{valor:.6g}" for valor in fila) for fila in matrix])

    def _format_vector(self, vector):
        return ", ".join(f"{valor:.6g}" for valor in vector)

    def _mostrar_procedimiento(self, metodo, resultado):
        t = self.text_proc
        t.insert("end", f"MÉTODO: {metodo}\n\n")
        t.insert("end", "Matriz A:\n")
        t.insert("end", self._format_matrix(resultado["A"]) + "\n\n")
        t.insert("end", "Vector b:\n")
        t.insert("end", self._format_vector(resultado["b"]) + "\n\n")

        if metodo == "Gauss-Seidel":
            t.insert("end", f"Aproximación inicial x0: {self._format_vector(resultado['x0'])}\n\n")
            for paso in resultado["historial"]:
                t.insert("end", paso["detalle"] + "\n")
            t.insert("end", f"\nSOLUCIÓN FINAL: {self._format_vector(resultado['solucion'])}\n")
            t.insert("end", f"ERROR FINAL: {resultado['error']:.6g}\n")
        else:
            for paso in resultado["historial"]:
                t.insert("end", paso["detalle"] + "\n")
            if resultado["x"] is not None:
                t.insert("end", f"\nSUSTITUCIÓN DIRECTA Y REGRESIVA:\n")
                t.insert("end", f"y = {self._format_vector(resultado['y'])}\n")
                t.insert("end", f"x = {self._format_vector(resultado['x'])}\n")

    def _exportar_pdf(self):
        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Primero calcula")
            return

        doc = SimpleDocTemplate(
            "sistemas_lineales.pdf",
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
        contenido.append(Paragraph("SISTEMAS LINEALES", estilo_titulo))
        contenido.append(Paragraph(f"Ejercicio: {self.var_met.get()}", estilo_subtitulo))

        datos = [
            ["Método:", self.var_met.get()],
            ["Vector b:", self._format_vector(self.ultimo_resultado["b"])],
        ]

        if self.var_met.get() == "Gauss-Seidel":
            datos.extend([
                ["Aproximación inicial:", self._format_vector(self.ultimo_resultado["x0"])],
                ["Iteraciones:", str(self.ultimo_resultado["iteraciones"])],
                ["Error final:", f"{self.ultimo_resultado['error']:.6g}"]
            ])
        else:
            datos.append(["Solución:", self._format_vector(self.ultimo_resultado["x"])])

        tabla_datos = Table(datos, colWidths=[150, 320])
        tabla_datos.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        contenido.append(tabla_datos)
        contenido.append(Spacer(1, 20))
        contenido.append(Paragraph("Matriz A", estilo_subtitulo))

        tabla_a = [[f"x{j+1}" for j in range(len(self.ultimo_resultado["A"][0]))]]
        for fila in self.ultimo_resultado["A"]:
            tabla_a.append([f"{valor:.6g}" for valor in fila])

        tabla_matriz = Table(tabla_a, colWidths=[80] * len(tabla_a[0]))
        tabla_matriz.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5597")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        contenido.append(tabla_matriz)
        contenido.append(PageBreak())

        contenido.append(Paragraph("Desarrollo del método", estilo_titulo))
        contenido.append(Spacer(1, 10))

        for paso in self.ultimo_resultado["historial"]:
            contenido.append(Paragraph(f"<b>Paso {paso['iter']}:</b>", estilo_normal))
            contenido.append(Paragraph(paso["detalle"].replace("\n", "<br/>"), estilo_normal))
            contenido.append(Spacer(1, 12))

        doc.build(contenido)
        messagebox.showinfo("PDF", "Generado correctamente")
