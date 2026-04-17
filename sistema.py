from flask import Flask, render_template, request, redirect
import json
import datetime
import webbrowser
import urllib.parse

app = Flask(__name__)

archivo = "leads.json"

# -------------------------
# BASE
# -------------------------

def cargar_leads():
    try:
        with open(archivo, "r") as f:
            return json.load(f)
    except:
        return []

def guardar_leads(leads):
    with open(archivo, "w") as f:
        json.dump(leads, f, indent=4)

# -------------------------
# MENSAJE
# -------------------------

def generar_mensaje(lead):
    return f"Hola {lead['nombre']} 👋 ¿Te gustaría automatizar tus ventas?"

# -------------------------
# RUTAS
# -------------------------

@app.route("/")
def index():
    leads = cargar_leads()
    return render_template("index.html", leads=leads)

# 👉 CREAR LEAD REAL
@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        leads = cargar_leads()

        leads.append({
            "nombre": nombre,
            "telefono": telefono,
            "estado": "nuevo",
            "fecha": str(datetime.date.today())
        })

        guardar_leads(leads)
        return redirect("/")

    return render_template("nuevo.html")

# 👉 CAMBIAR ESTADO
@app.route("/estado/<int:i>/<estado>")
def cambiar_estado(i, estado):
    leads = cargar_leads()
    leads[i]["estado"] = estado
    guardar_leads(leads)
    return redirect("/")

# 👉 ELIMINAR
@app.route("/eliminar/<int:i>")
def eliminar(i):
    leads = cargar_leads()
    leads.pop(i)
    guardar_leads(leads)
    return redirect("/")

# 👉 WHATSAPP
@app.route("/abrir/<int:i>")
def abrir(i):
    leads = cargar_leads()
    lead = leads[i]

    mensaje = generar_mensaje(lead)
    texto = urllib.parse.quote(mensaje)
    url = f"https://wa.me/{lead['telefono']}?text={texto}"

    webbrowser.open(url)
    return redirect("/")

# -------------------------

app.run(debug=True)
