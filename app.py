from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Fuentes únicas de datos (mock)

def get_orders():
    return [
        {"code": "OR-00123", "client": "María Gómez", "vehicle": "Toyota Corolla (ABC-123)", "tech": "Luis Pérez", "status": "En Diagnóstico", "date": "2025-10-20"},
        {"code": "OR-00124", "client": "Carlos Ruiz", "vehicle": "Nissan Versa (XYZ-789)", "tech": "Ana Torres", "status": "En Progreso", "date": "2025-10-21"},
        {"code": "OR-00125", "client": "Laura Méndez", "vehicle": "Mazda 3 (JKL-456)", "tech": "Pedro Silva", "status": "Esperando Aprobación", "date": "2025-10-21"},
    ]

def get_items():
    return [
        {"code": "P-0001", "product": "Aceite 5W30 1L", "category": "Lubricantes", "brand": "Castrol", "qty": 24, "minmax": "10/100", "price": "$35.00", "loc": "A1-01", "status": "Normal"},
        {"code": "P-0002", "product": "Filtro de Aceite", "category": "Filtros", "brand": "Bosch", "qty": 8, "minmax": "15/60", "price": "$18.00", "loc": "A1-05", "status": "Bajo Stock"},
        {"code": "P-0003", "product": "Pastillas de Freno", "category": "Frenos", "brand": "ACDelco", "qty": 12, "minmax": "8/50", "price": "$45.00", "loc": "B2-03", "status": "Normal"},
    ]

def get_invoices():
    return [
        {"no": "F-00045", "order": "OR-00120", "client": "María Gómez", "emit": "2025-10-01", "due": "2025-10-15", "subtotal": "$1,000", "vat": "$160", "total": "$1,160", "state": "Pagada"},
        {"no": "F-00046", "order": "OR-00121", "client": "Carlos Ruiz", "emit": "2025-10-05", "due": "2025-10-20", "subtotal": "$850", "vat": "$136", "total": "$986", "state": "Pendiente"},
        {"no": "F-00047", "order": "OR-00119", "client": "Laura Méndez", "emit": "2025-09-25", "due": "2025-10-05", "subtotal": "$300", "vat": "$48", "total": "$348", "state": "Vencida"},
    ]

# Credenciales simples para prototipo
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")

# Decorador para requerir login

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Debes iniciar sesión", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped

# Página de inicio: dashboard
@app.route("/")
@login_required
def home():
    metrics = {
        "vehicles_today": 5,
        "day_income": "$1,250",
        "pending_approval": 3,
    }

    orders = get_orders()

    return render_template("dashboard.html", metrics=metrics, orders=orders)

# Secciones principales
@app.route("/clientes")
@login_required
def clientes():
    totals = {"total": 128, "active": 97, "vehicles": 182}
    clients = get_clients()
    return render_template("clientes.html", totals=totals, clients=clients)

# Utilidad para clientes

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text).strip("-")
    return text


def get_clients():
    base = [
        {"name": "María Gómez", "email": "maria@example.com", "phone": "+57 300 111 2233", "vehicles": 2, "orders": 5, "last": "2025-10-20", "state": "Activo"},
        {"name": "Carlos Ruiz", "email": "carlos@example.com", "phone": "+57 301 222 3344", "vehicles": 1, "orders": 2, "last": "2025-10-18", "state": "Activo"},
        {"name": "Laura Méndez", "email": "laura@example.com", "phone": "+57 302 333 4455", "vehicles": 3, "orders": 8, "last": "2025-10-10", "state": "Inactivo"},
    ]
    for c in base:
        c["slug"] = slugify(c["name"])
    return base

@app.route("/inventario")
@login_required
def inventario():
    totals = {"count": 42, "value": "$7,980", "low": 5, "cats": 9}
    items = get_items()
    return render_template("inventario.html", totals=totals, items=items)

@app.route("/inventario/<code>/editar")
@login_required
def inventario_editar(code):
    # Buscar el item por código en los datos de ejemplo
    items = get_items()
    catalog = {i["code"]: i for i in items}
    item = catalog.get(code)
    if not item:
        flash("Producto no encontrado", "warning")
        return redirect(url_for("inventario"))
    return render_template("inventario_editar.html", item=item)

@app.route("/inventario/exportar")
@login_required
def inventario_exportar():
    # CSV básico de ejemplo
    items = get_items()
    rows = [
        ["code","product","category","brand","qty","minmax","price","loc","status"],
        *[[i["code"], i["product"], i["category"], i["brand"], i["qty"], i["minmax"], i["price"], i["loc"], i["status"]] for i in items]
    ]
    csv = "\n".join([",".join(map(str, r)) for r in rows])
    from flask import Response
    return Response(csv, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=inventario.csv"})

@app.route("/ordenes")
@login_required
def ordenes():
    orders = get_orders()
    return render_template("ordenes.html", orders=orders)

# Aliases para compatibilidad con href antiguos
@app.route("/nueva-orden")
@login_required
def alias_nueva_orden():
    return redirect(url_for("form_nueva_orden"))

# Detalle de orden (placeholder)
@app.route("/ordenes/<code>")
@login_required
def orden_detalle(code):
    order = next((o for o in get_orders() if o["code"] == code), None)
    if not order:
        flash("Orden no encontrada", "warning")
        return redirect(url_for("ordenes"))
    # Por ahora solo mostramos un detalle mínimo
    return render_template("ordenes.html", orders=[order])

@app.route("/agendar-cita")
@login_required
def alias_agendar_cita():
    return redirect(url_for("form_nueva_cita"))

@app.route("/nueva-cita")
@login_required
def alias_nueva_cita():
    return redirect(url_for("form_nueva_cita"))

@app.route("/nuevo-cliente")
@login_required
def alias_nuevo_cliente():
    return redirect(url_for("form_nuevo_cliente"))

@app.route("/clientes/<slug>")
@login_required
def cliente_detalle(slug):
    clients = get_clients()
    catalog = {c["slug"]: c for c in clients}
    client = catalog.get(slug)
    if not client:
        flash("Cliente no encontrado", "warning")
        return redirect(url_for("clientes"))
    return render_template("cliente_detalle.html", client=client)

@app.route("/agregar-producto")
@login_required
def alias_agregar_producto():
    return redirect(url_for("form_agregar_producto"))

@app.route("/nueva-factura")
@login_required
def alias_nueva_factura():
    return redirect(url_for("form_nueva_factura"))

@app.route("/facturacion")
@login_required
def facturacion():
    summary = {"total": "$12,450", "paid": "$9,200", "due": "$2,800", "overdue": "$450"}
    invoices = get_invoices()
    return render_template("facturacion.html", summary=summary, invoices=invoices)

@app.route("/facturacion/exportar")
@login_required
def facturacion_exportar():
    invoices = get_invoices()
    rows = [
        ["no","order","client","emit","due","subtotal","vat","total","state"],
        *[[f["no"], f["order"], f["client"], f["emit"], f["due"], f["subtotal"], f["vat"], f["total"], f["state"]] for f in invoices]
    ]
    csv = "\n".join([",".join(map(str, r)) for r in rows])
    from flask import Response
    return Response(csv, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=facturacion.csv"})

# Formularios
@app.route("/clientes/nuevo")
@login_required
def form_nuevo_cliente():
    return render_template("form_nuevo_cliente.html")

@app.route("/citas/nueva")
@login_required
def form_nueva_cita():
    return render_template("form_nueva_cita.html")

@app.route("/ordenes/nueva")
@login_required
def form_nueva_orden():
    return render_template("form_nueva_orden.html")

@app.route("/facturas/nueva")
@login_required
def form_nueva_factura():
    return render_template("form_nueva_factura.html")

@app.route("/facturas/<no>")
@login_required
def factura_detalle(no):
    # Reutilizar fuente única de facturas
    invoices = get_invoices()
    catalog = {f["no"]: f for f in invoices}
    factura = catalog.get(no)
    if not factura:
        flash("Factura no encontrada", "warning")
        return redirect(url_for("facturacion"))
    return render_template("factura_detalle.html", factura=factura)

@app.route("/productos/nuevo")
@login_required
def form_agregar_producto():
    return render_template("form_agregar_producto.html")

# Agenda (si existe plantilla agenda.html)
@app.route("/agenda")
@login_required
def agenda():
    return render_template("agenda.html")

# Autenticación
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        next_url = request.args.get("next") or url_for("home")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["user_id"] = username
            flash("Bienvenido, administrador", "success")
            return redirect(next_url)
        else:
            flash("Credenciales inválidas", "danger")
            # conservar next en la query
            return redirect(url_for("login", next=next_url))
    # GET
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
