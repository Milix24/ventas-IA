from flask import Flask, render_template, request, redirect
import sqlite3
import webbrowser
import urllib.parse

app = Flask(__name__)

# -------------------------
# BASE DE DATOS
# -------------------------

def conectar():
    conn = sqlite3.connect("ventas.db")
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla():
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            estado TEXT,
            nota TEXT
        )
    """)
    conn.commit()
    conn.close()

crear_tabla()

# -------------------------
# MENSAJES INTELIGENTES
# -------------------------

def generar_mensaje(lead):
    if lead["estado"] == "nuevo":
        return f"Hola {lead['nombre']} 👋 vi tu negocio y creo que podrías automatizar tus ventas. ¿Te explico rápido?"
    elif lead["estado"] == "contactado":
        return f"Hola {lead['nombre']} 😊 solo paso para saber si viste mi mensaje anterior."
    elif lead["estado"] == "interesado":
        return f"Hola {lead['nombre']} 🔥 ¿avanzamos hoy con la automatización?"
    return f"Hola {lead['nombre']} 👋"

def sugerencias(leads):
    lista = []
    for lead in leads:
        if lead["estado"] == "nuevo":
            accion = "Primer contacto"
        elif lead["estado"] == "contactado":
            accion = "Seguimiento"
        elif lead["estado"] == "interesado":
            accion = "Cerrar venta"
        else:
            accion = "Revisar"

        lista.append({
            "lead": lead,
            "accion": accion,
            "mensaje": generar_mensaje(lead)
        })
    return lista

# -------------------------
# RUTAS
# -------------------------

@app.route("/")
def index():
    conn = conectar()
    leads = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()
    return render_template("index.html", leads=leads)

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        conn = conectar()
        conn.execute(
            "INSERT INTO leads (nombre, telefono, estado, nota) VALUES (?, ?, ?, ?)",
            (nombre, telefono, "nuevo", "")
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("nuevo.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        nota = request.form["nota"]

        conn.execute(
            "UPDATE leads SET nombre=?, telefono=?, nota=? WHERE id=?",
            (nombre, telefono, nota, id)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    lead = conn.execute("SELECT * FROM leads WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("editar.html", lead=lead)

@app.route("/estado/<int:id>/<estado>")
def cambiar_estado(id, estado):
    conn = conectar()
    conn.execute("UPDATE leads SET estado=? WHERE id=?", (estado, id))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = conectar()
    conn.execute("DELETE FROM leads WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/abrir/<int:id>")
def abrir(id):
    conn = conectar()
    lead = conn.execute("SELECT * FROM leads WHERE id=?", (id,)).fetchone()
    conn.close()

    mensaje = generar_mensaje(lead)
    texto = urllib.parse.quote(mensaje)
    url = f"https://wa.me/{lead['telefono']}?text={texto}"

    webbrowser.open(url)
    return redirect("/")

@app.route("/inteligencia")
def inteligencia():
    conn = conectar()
    leads = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()

    data = sugerencias(leads)

    return render_template("inteligencia.html", data=data)

# -------------------------
# IMPORTANTE PARA INTERNET
# -------------------------

if __name__ == "__main__":
    app.run()

