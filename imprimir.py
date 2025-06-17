import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from bd_ruta import ruta_db
import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import win32print
import win32api
from reportlab.lib.pagesizes import inch
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img-and-sounds")
PDF_OUTPUT = os.path.join(BASE_DIR, "equipo_etiqueta.pdf")

ICON_MAP = {
    "Modelo": "device.png",
    "Comentario": "comentarios.png",
    "Sistema operativo": "sistema-operativo.png",
    "CPU": "cpu.png",
    "RAM": "ram.png",
    "Placa base": "placa-base.png",
    "Gráfica": "grafica.png",
    "Almacenamiento": "almacenamiento.png",
    "Unidades ópticas": "unidades-opticas.png",
    "Audio": "audio.png"
}

def crear_pdf(datos, icon_map, img_dir, output_path=PDF_OUTPUT):


    c = canvas.Canvas(output_path, pagesize=(4*inch, 6*inch))
    x_icon = 10
    x_text = x_icon + 20
    y = 6 * inch - 28
    icon_size = 16

    serial = datos.get('Serial', '')
    if serial and serial.strip():
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_icon, y, f"Serial: {serial}")
        y -= 15

    comentario = datos.get('Comentario', '')
    if comentario and comentario.strip():
        # Modelo
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_icon, y, f"Modelo: {datos.get('Modelo', '')}")
        y -= 15
        # Comentario
        c.setFont("Helvetica", 10)
        c.drawString(x_icon, y, f"Comentario: {comentario}")
        y -= 26
    else:
        # Solo Modelo (y salto grande)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_icon, y, f"Modelo: {datos.get('Modelo', '')}")
        y -= 20

    # Campos con íconos y títulos compactos
    for key in ["Sistema operativo", "CPU", "RAM", "Placa base", "Gráfica", "Almacenamiento", "Unidades ópticas", "Audio"]:
        val = datos.get(key, "")
        icon_file = icon_map.get(key, "")
        icon_path = os.path.join(img_dir, icon_file)
        if os.path.isfile(icon_path):
            c.drawImage(ImageReader(icon_path), x_icon, y - 1, width=icon_size, height=icon_size, mask='auto')
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x_text, y+2, f"{key}:")
        y -= 6  # Menor espacio entre título y descripción

        c.setFont("Helvetica", 6)
        if isinstance(val, list):
            for line in val:
                c.drawString(x_text + 8, y, f"• {line}")
                y -= 7  # Menor espacio entre líneas de descripción
        else:
            c.drawString(x_text + 8, y, str(val))
            y -= 9

        y -= 10   # Espacio extra final para separar bloques

        if y < 40:
            c.showPage()
            y = 6 * inch - 28

    c.save()

def imprimir_pdf_en_impresora(pdf_path, nombre_impresora="LABEL_IMAXIS"):
    # Convertir la ruta del PDF a absoluta
    abs_path = os.path.abspath(pdf_path)
    
    # Buscar la impresora que coincida con el nombre especificado
    impresoras = [p[2] for p in win32print.EnumPrinters(2)]
    seleccionada = None
    for imp in impresoras:
        if nombre_impresora.lower() in imp.lower():
            seleccionada = imp
            break
    if not seleccionada:
        raise Exception(f"No se encontró una impresora que contenga '{nombre_impresora}'.\nImpresoras detectadas:\n" + "\n".join(impresoras))
    
    # Ruta al ejecutable PDFtoPrinter.exe (en la misma carpeta que el script)
    pdf_to_printer_path = os.path.join(BASE_DIR, "PDFtoPrinter.exe")
    if not os.path.exists(pdf_to_printer_path):
        raise Exception("PDFtoPrinter.exe no se encuentra en la ruta especificada.")
    
    # Comando para imprimir el PDF
    comando = [
        pdf_to_printer_path,
        abs_path,
        seleccionada
    ]
    
    # Ejecutar el comando y manejar errores
    try:
        subprocess.run(comando, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error al imprimir con PDFtoPrinter: {e}")

def obtener_datos_completos(serial):
    try:
        conn = mysql.connector.connect(**ruta_db)
        cur = conn.cursor()
        cur.execute("SELECT id, modelo, comentario FROM equipo WHERE serial=%s", (serial,))
        equipo = cur.fetchone()
        if not equipo:
            cur.close()
            conn.close()
            return None
        equipo_id, modelo, comentario = equipo

        datos = {"Serial": serial, "Modelo": modelo or "", "Comentario": comentario or ""}

        cur.execute("SELECT sistema, cpu, placa_base FROM info_estatica WHERE equipo_id=%s", (equipo_id,))
        est = cur.fetchone()
        if est:
            datos["Sistema operativo"], datos["CPU"], datos["Placa base"] = est
        else:
            datos["Sistema operativo"] = datos["CPU"] = datos["Placa base"] = ""

        def get_list(tabla):
            cur.execute(f"SELECT descripcion FROM {tabla} WHERE equipo_id=%s", (equipo_id,))
            return [row[0] for row in cur.fetchall()]

        datos["RAM"] = get_list("ram")
        datos["Gráfica"] = get_list("grafica")
        datos["Almacenamiento"] = get_list("almacenamiento")
        datos["Unidades ópticas"] = get_list("opticas")
        datos["Audio"] = get_list("audio")
        cur.close()
        conn.close()
        return datos
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información completa:\n{e}")
        return None

def cargar_ultimos(tree):
    tree.delete(*tree.get_children())
    try:
        conn = mysql.connector.connect(**ruta_db)
        cursor = conn.cursor()
        query = """
            SELECT e.serial, e.modelo, i.cpu, i.placa_base, e.fecha
            FROM equipo e
            LEFT JOIN info_estatica i ON e.id = i.equipo_id
            ORDER BY e.fecha DESC
            LIMIT 10
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo cargar la información:\n{e}")

def actualizar_periodico(tree, root):
    cargar_ultimos(tree)
    root.after(5000, lambda: actualizar_periodico(tree, root))

def imprimir_registro(tree):
    item_id = tree.focus()
    if not item_id:
        messagebox.showwarning("Selecciona", "Selecciona un registro para imprimir.")
        return
    valores = tree.item(item_id)["values"]
    if not valores:
        return
    serial = valores[0]
    datos = obtener_datos_completos(serial)
    if not datos:
        return
    crear_pdf(datos, ICON_MAP, IMG_DIR)
    try:
        imprimir_pdf_en_impresora(PDF_OUTPUT, "LABEL_IMAXIS")
        messagebox.showinfo("Impresión", "Etiqueta enviada a la impresora Epson.")
    except Exception as e:
        messagebox.showerror("Impresión fallida", f"No se pudo imprimir automáticamente:\n{e}\nAbriendo PDF para impresión manual.")
        try:
            pass
            #os.startfile(PDF_OUTPUT)
        except Exception:
            messagebox.showinfo("PDF generado", f"PDF creado: {PDF_OUTPUT}\nPuedes abrirlo y enviarlo a imprimir.")

import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Imprimir etiqueta de equipo")
    root.resizable(False, False)

    fondo = "#1E1E1E"
    texto = "#E0E0E0"
    azul = "#228be6"

    # Fondo global
    root.configure(bg=fondo)

    # --------- Estilo ttk modo noche ---------
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background=fondo, foreground=texto, fieldbackground=fondo)
    style.configure("Treeview",
        background=fondo, foreground=texto,
        fieldbackground=fondo, bordercolor="#222",
        rowheight=28, font=("Segoe UI", 11)
    )
    style.configure("Treeview.Heading",
        background="#232323", foreground="#fff", font=("Segoe UI", 11, "bold"),
        bordercolor="#333"
    )
    style.map("Treeview", background=[("selected", "#353d4d")])
    style.configure("TLabelframe", background=fondo, foreground=texto)
    style.configure("TLabelframe.Label", background=fondo, foreground=texto)

    # ------- Layout -------
    w, h = 850, 500
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    frame_lista = ttk.LabelFrame(root, text="Últimos equipos (10)", style="TLabelframe")
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Serial", "Modelo", "CPU", "Placa", "Fecha")
    tree = ttk.Treeview(frame_lista, columns=columns, show="headings", style="Treeview")
    tree.pack(fill="both", expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", stretch=True, width=150)

    cargar_ultimos(tree)
    root.after(5000, lambda: actualizar_periodico(tree, root))

    btn_print = tk.Button(
        root, text="Imprimir etiqueta", font=("Segoe UI", 12, "bold"),
        bg=azul, fg="white", activebackground="#17416b", activeforeground="#fff",
        bd=0, highlightbackground=azul, highlightcolor=azul, relief="flat"
    )
    btn_print.config(command=lambda: imprimir_registro(tree))
    btn_print.pack(pady=8)

    root.mainloop()


if __name__ == "__main__":
    main()
