
from flask import Flask, render_template, request, redirect, jsonify
import heapq

app = Flask(__name__)

class Paciente:
    def __init__(self, ticket, cedula):
        self.ticket = ticket
        self.cedula = cedula
        self.nombre = ""
        self.edad = ""
        self.motivo = ""
        self.gravedad = None
        self.especialidad = None

    def __lt__(self, other):
        return self.gravedad < other.gravedad


ticket_actual = 1

cola_kiosko = []
cola_recepcion = []

colas_finales = {
    "cirujano": {"prioridad": []},
    "cardiologo": {"prioridad": []},
    "maxilo": {"prioridad": []},
    "otros": {"prioridad": []}
}


@app.route("/")
def index():
    return render_template(
        "index.html",
        kiosko=cola_kiosko,
        recepcion=cola_recepcion,
        finales=colas_finales
    )


@app.route("/data")
def data():
    return jsonify({
        "finales": {
            esp: [
                {"ticket": p.ticket, "nombre": p.nombre, "gravedad": p.gravedad}
                for p in sorted(colas_finales[esp]["prioridad"])
            ]
            for esp in colas_finales
        }
    })


@app.route("/kiosko", methods=["POST"])
def kiosko():
    global ticket_actual

    cedula = request.form.get("cedula")
    if not cedula:
        return redirect("/")

    p = Paciente(ticket_actual, cedula)
    cola_kiosko.append(p)

    ticket_actual += 1
    return redirect("/")


@app.route("/pasar_recepcion")
def pasar_recepcion():
    if cola_kiosko:
        paciente = cola_kiosko.pop(0)
        cola_recepcion.append(paciente)

    return redirect("/")


@app.route("/recepcion/<int:ticket>", methods=["POST"])
def recepcion(ticket):
    for p in cola_recepcion:
        if p.ticket == ticket:
            p.nombre = request.form.get("nombre", "")
            p.edad = request.form.get("edad", "")
            p.motivo = request.form.get("motivo", "")
            break

    return redirect("/")


@app.route("/triage/<int:ticket>", methods=["POST"])
def triage(ticket):
    for i, p in enumerate(cola_recepcion):
        if p.ticket == ticket:

            gravedad = request.form.get("gravedad")
            if not gravedad:
                return redirect("/")

            p.gravedad = int(gravedad)
            p.especialidad = request.form.get("especialidad")

            # SOLO prioridad alta pasa a especialista
            if p.gravedad <= 3:
                cola_recepcion.pop(i)
                heapq.heappush(colas_finales[p.especialidad]["prioridad"], p)

            break

    return redirect("/")


@app.route("/atender/<esp>")
def atender(esp):
    if colas_finales[esp]["prioridad"]:
        heapq.heappop(colas_finales[esp]["prioridad"])

    # 👇 ALERTA
    return redirect("/?msg=atendido")


if __name__ == "__main__":
    app.run(debug=True)
