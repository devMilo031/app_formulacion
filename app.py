from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import os
import re

# Lista global (simula base de datos en memoria)
clientes_data = [
    {"name": "María Gómez", "email": "maria@example.com", "phone": "+57 300 111 2233", "vehicles": 2, "orders": 5, "last": "2025-10-20", "state": "Activo"},
    {"name": "Carlos Ruiz", "email": "carlos@example.com", "phone": "+57 301 222 3344", "vehicles": 1, "orders": 2, "last": "2025-10-18", "state": "Activo"},
    {"name": "Laura Méndez", "email": "laura@example.com", "phone": "+57 302 333 4455", "vehicles": 3, "orders": 8, "last": "2025-10-10", "state": "Inactivo"},
]

productos = [
    {"code": "P-0001", "product": "Aceite 5W30 1L", "category": "Lubricantes", "brand": "Castrol", "qty": 24, "minmax": "10/100", "price": "$35.00", "loc": "A1-01", "status": "Normal"},
    {"code": "P-0002", "product": "Filtro de Aceite", "category": "Filtros", "brand": "Bosch", "qty": 8, "minmax": "15/60", "price": "$18.00", "loc": "A1-05", "status": "Bajo Stock"},
    {"code": "P-0003", "product": "Pastillas de Freno", "category": "Frenos", "brand": "ACDelco", "qty": 12, "minmax": "8/50", "price": "$45.00", "loc": "B2-03", "status": "Normal"},
]
orders = [
        {"code": "OR-00123", "client": "María Gómez", "vehicle": "Toyota Corolla (ABC-123)", "tech": "Luis Pérez", "status": "En Diagnóstico", "date": "2025-10-20"},
        {"code": "OR-00124", "client": "Carlos Ruiz", "vehicle": "Nissan Versa (XYZ-789)", "tech": "Ana Torres", "status": "En Progreso", "date": "2025-10-21"},
        {"code": "OR-00125", "client": "Laura Méndez", "vehicle": "Mazda 3 (JKL-456)", "tech": "Pedro Silva", "status": "Esperando Aprobación", "date": "2025-10-21"},
    ]
invoices_data = [
        {"no": "F-00045", "order": "OR-00120", "client": "María Gómez", "emit": "2025-10-01", "due": "2025-10-15", "subtotal": "$1,000", "vat": "$160", "total": "$1,160", "state": "Pagada"},
        {"no": "F-00046", "order": "OR-00121", "client": "Carlos Ruiz", "emit": "2025-10-05", "due": "2025-10-20", "subtotal": "$850", "vat": "$136", "total": "$986", "state": "Pendiente"},
        {"no": "F-00047", "order": "OR-00119", "client": "Laura Méndez", "emit": "2025-09-25", "due": "2025-10-05", "subtotal": "$300", "vat": "$48", "total": "$348", "state": "Vencida"},
    ]
citas=[]
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# Fuentes únicas de datos (mock)

def get_orders():
    return orders

def get_items():
    return productos

def get_invoices():
    return invoices_data

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


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text).strip("-")
    return text

def get_clients():
    """Devuelve la lista de clientes con un slug único para cada uno"""
    for c in clientes_data:
        c["slug"] = slugify(c["name"])
    return clientes_data


@app.route("/clientes")
@login_required
def clientes():
    """Página principal de clientes"""
    totals = {
        "total": len(clientes_data),
        "active": sum(1 for c in clientes_data if c["state"] == "Activo"),
        "vehicles": sum(c["vehicles"] for c in clientes_data),
    }
    clients = get_clients()
    return render_template("clientes.html", totals=totals, clients=clients)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def form_nuevo_cliente():
    """Formulario para agregar un nuevo cliente"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not email:
            flash("El nombre y el correo son obligatorios", "warning")
            return redirect(url_for("form_nuevo_cliente"))

        nuevo_cliente = {
            "name": name,
            "email": email,
            "phone": phone or "N/A",
            "vehicles": 0,
            "orders": 0,
            "last": "2025-11-01",
            "state": "Activo",
        }

        clientes_data.append(nuevo_cliente)
        flash(f"Cliente '{name}' agregado correctamente", "success")
        return redirect(url_for("clientes"))

    return render_template("form_nuevo_cliente.html")

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

# # Formularios
# @app.route("/clientes/nuevo")
# @login_required
# def form_nuevo_cliente():
#     return render_template("form_nuevo_cliente.html")

@app.route("/citas/nueva", methods=["GET", "POST"])
@login_required
def form_nueva_cita():
    if request.method == "POST":
        # Obtener los datos del formulario
        client = request.form["client"]
        service = request.form["service"]
        date = request.form["date"]
        time = request.form["time"]

        # Generar código automático para la nueva cita
        new_code = f"CITA-{len(citas) + 1:04d}"  # Ej: CITA-0001, CITA-0002, etc.

        # Crear el diccionario con la nueva cita
        nueva_cita = {
            "code": new_code,
            "client": client,
            "service": service,
            "date": date,
            "time": time,
            "status": "Pendiente"
        }

        # Guardarla en la lista global
        citas.append(nueva_cita)

        flash(f"Cita '{new_code}' agendada correctamente para {client}.", "success")
        return redirect(url_for("agenda"))  # Redirige al listado de citas o agenda

    # Si es GET, renderiza el formulario
    return render_template("form_nueva_cita.html")

@app.route("/ordenes/nueva", methods=["GET", "POST"])
@login_required
def form_nueva_orden():
    if request.method == "POST":
        # Obtener los valores del formulario
        client = request.form["client"]
        vehicle = request.form["vehicle"]
        tech = request.form["tech"]

        # Generar código automático para la nueva orden
        new_code = f"OR-{len(orders) + 123:05d}"  # Ej: OR-00126

        # Crear la nueva orden
        nueva_orden = {
            "code": new_code,
            "client": client,
            "vehicle": vehicle,
            "tech": tech,
            "status": "Pendiente",
            "date": "2025-11-02"
        }

        # Guardarla en la lista global
        orders.append(nueva_orden)

        flash(f"Orden '{new_code}' creada correctamente para {client}.", "success")
        return redirect(url_for("ordenes"))

    # Si es un GET, solo renderiza el formulario
    return render_template("form_nueva_orden.html")

@app.route("/facturas/nueva", methods=["GET", "POST"])
@login_required
def form_nueva_factura():
    if request.method == "POST":
        order = request.form["order"]
        client = request.form["client"]
        subtotal = float(request.form["subtotal"])
        due_date = request.form["due_date"]

        new_code = f"FAC-{len(invoices_data) + 1:04d}"
        nueva_factura = {
            "code": new_code,
            "order": order,
            "client": client,
            "subtotal": subtotal,
            "due_date": due_date,
            "status": "Pendiente"
        }
        invoices_data.append(nueva_factura)
        flash(f"Factura '{new_code}' creada correctamente.", "success")
        return redirect(url_for("facturacion"))  # o donde muestres las facturas

    # 🔹 Aquí está la clave: pasar las listas
    return render_template(
        "form_nueva_factura.html",
        orders=orders,     # lista de órdenes
        clients=clientes_data    # lista de clientes
    )

@app.route("/facturas/<no>")
@login_required
def factura_detalle(no):
    # Reutilizar fuente única de facturas
    invoices = get_invoices()
    print(invoices)
    catalog = {f["no"]: f for f in invoices}
    factura = catalog.get(no)
    if not factura:
        flash("Factura no encontrada", "warning")
        return redirect(url_for("facturacion"))
    return render_template("factura_detalle.html", factura=factura)

@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def form_agregar_producto():
    if request.method == "POST":
        # Obtener los datos del formulario
        product = request.form["product"]
        category = request.form["category"]
        brand = request.form["brand"]
        qty = int(request.form["qty"])
        min_qty = int(request.form["min_qty"])
        max_qty = int(request.form["max_qty"])
        price = float(request.form["price"])
        location = request.form["location"]

        # Generar código automático para el nuevo producto
        new_code = f"P-{len(productos) + 1:04d}"

        # Determinar el estado según stock
        if qty < min_qty:
            status = "Bajo Stock"
        elif qty > max_qty:
            status = "Exceso"
        else:
            status = "Normal"

        # Crear texto del rango min/max
        minmax = f"{min_qty}/{max_qty}"

        # Agregar el producto a la lista global
        productos.append({
            "code": new_code,
            "product": product,
            "category": category,
            "brand": brand,
            "qty": qty,
            "minmax": minmax,
            "price": f"${price:.2f}",
            "loc": location,
            "status": status
        })

        flash(f"Producto '{product}' agregado exitosamente.", "success")
        return redirect(url_for("inventario"))  # O a tu ruta principal del inventario

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
