# abrir.py
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from bd_ruta import ruta_db
import os

def abrir_y_cargar(callback=None):
    root = tk.Toplevel()
    root.withdraw()  # Ocultar temporalmente para evitar parpadeo
    root.title("Abrir equipo")
    root.resizable(False, False)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(BASE_DIR, 'img-and-sounds', 'icono.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    # Modo oscuro (global)
    fondo = "#1E1E1E"
    texto = "#E0E0E0"

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background=fondo, foreground=texto, fieldbackground=fondo)
    style.configure("Treeview", background=fondo, foreground=texto, fieldbackground=fondo)
    style.configure("Treeview.Heading", background="#2C2C2C", foreground="#FFFFFF")
    style.map("Treeview", background=[("selected", "#444444")])

    # Definir tamaño y centrar ANTES de mostrar
    w, h = 800, 500
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.configure(bg=fondo)
    root.deiconify()  # Mostrar ventana ya centrada

    # Frame superior: búsqueda por serial
    frame_equipo = ttk.LabelFrame(root, text="Equipo")
    frame_equipo.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_equipo, text="Serial:").pack(side="left", padx=5, pady=5)
    serial_entry = tk.Entry(frame_equipo, width=30, bg="#1E1E1E", fg="#E0E0E0", insertbackground="white")
    serial_entry.pack(side="left", padx=5)
    serial_entry.focus_set()

    # Frame inferior: listado de equipos
    frame_lista = ttk.LabelFrame(root, text="Equipos")
    frame_lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    columns = ("Serial", "Modelo", "CPU", "Placa", "Fecha")
    tree = ttk.Treeview(frame_lista, columns=columns, show="headings")
    tree.pack(fill="both", expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", stretch=True)

    def cargar_equipos(filtro_serial=None):
        tree.delete(*tree.get_children())
        try:
            conn = mysql.connector.connect(**ruta_db)
            cursor = conn.cursor()
            if filtro_serial:
                query = """
                    SELECT e.serial, e.modelo, i.cpu, i.placa_base, e.fecha
                    FROM equipo e
                    LEFT JOIN info_estatica i ON e.id = i.equipo_id
                    WHERE e.serial LIKE %s
                    ORDER BY e.fecha DESC
                """
                cursor.execute(query, (f"%{filtro_serial}%",))
            else:
                query = """
                    SELECT e.serial, e.modelo, i.cpu, i.placa_base, e.fecha
                    FROM equipo e
                    LEFT JOIN info_estatica i ON e.id = i.equipo_id
                    ORDER BY e.fecha DESC
                """
                cursor.execute(query)

            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo cargar la información:\n{e}")

    # Activar búsqueda al presionar Enter
    serial_entry.bind("<Return>", lambda e: cargar_equipos(serial_entry.get().strip()))

    def on_doble_click(event):
        item_id = tree.focus()
        if not item_id:
            return
        valores = tree.item(item_id)["values"]
        if not valores:
            return
        serial = valores[0]
        root.destroy()
        if callback:
            callback(serial)

    tree.bind("<Double-1>", on_doble_click)

    cargar_equipos()
    root.mainloop()

if __name__ == "__main__":
    abrir_y_cargar()
