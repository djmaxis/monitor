import os, json, mysql.connector
from tkinter import messagebox, Tk
from bd_ruta import ruta_db

def guardar_desde_json():
    base_dir  = os.path.dirname(__file__)
    temp_path = os.path.join(base_dir, "temp_guardar.json")
    if not os.path.exists(temp_path):
        print("❌ JSON temporal no encontrado.")
        return

    payload       = json.load(open(temp_path, encoding="utf-8"))
    serial        = payload.get("serial","").strip()
    modelo        = payload.get("modelo","").strip()
    comentario    = payload.get("comentario","").strip()
    info_estatica = payload.get("info_estatica",{})
    listas        = payload.get("listas",{})

    if not serial:
        print("❌ Serial inválido.")
        return

    conn = mysql.connector.connect(**ruta_db)
    cur  = conn.cursor()

    # 1) ¿Existe?
    cur.execute("SELECT id FROM equipo WHERE serial=%s", (serial,))
    row = cur.fetchone()
    if row:
        equipo_id = row[0]
        # a) actualizar metadatos
        cur.execute("UPDATE equipo SET modelo=%s, comentario=%s WHERE id=%s",
                    (modelo, comentario, equipo_id))
        # b) borrar hijos
        cur.execute("DELETE FROM info_estatica WHERE equipo_id=%s", (equipo_id,))
        for t in ["ram","grafica","almacenamiento","opticas","audio"]:
            cur.execute(f"DELETE FROM {t} WHERE equipo_id=%s", (equipo_id,))
    else:
        # nuevo
        cur.execute("INSERT INTO equipo (serial, modelo, comentario) VALUES (%s,%s,%s)",
                    (serial, modelo, comentario))
        equipo_id = cur.lastrowid

    # 2) insertar estáticos
    cur.execute(
        "INSERT INTO info_estatica (equipo_id, sistema, cpu, placa_base) VALUES (%s,%s,%s,%s)",
        (equipo_id,
         info_estatica.get("sistema",""),
         info_estatica.get("cpu",""),
         info_estatica.get("placa_base",""))
    )

    # 3) insertar listas
    for tabla, items in listas.items():
        for linea in items:
            cur.execute(
                f"INSERT INTO {tabla} (equipo_id, descripcion) VALUES (%s,%s)",
                (equipo_id, linea)
            )

    conn.commit()
    cur.close()
    conn.close()
    os.remove(temp_path)

    try:
        root = Tk(); root.withdraw()
        messagebox.showinfo("Guardado", f"Equipo: '{serial}' guardado correctamente.")
        root.destroy()
    except:
        print(f"✅ Equipo '{serial}' guardado correctamente.")

if __name__ == "__main__":
    guardar_desde_json()
