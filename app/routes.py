from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Equipo, Mantenimiento
from datetime import datetime
from dateutil.relativedelta import relativedelta 


routes = Blueprint('routes', __name__)

# ============================================================
# 🟢 EQUIPOS
# ============================================================

from dateutil.relativedelta import relativedelta  #  para sumar meses fácilmente

@routes.route('/equipos', methods=['POST'])
def agregar_equipo():
    data = request.get_json() or {}

    # Validación básica
    campos_requeridos = ['nombre', 'marca', 'modelo', 'fecha_compra', 'periodo_mantenimiento', 'estado']
    for campo in campos_requeridos:
        if not data.get(campo):  # ahora también valida vacíos
            return jsonify({"error": f"Falta el campo requerido o está vacío: {campo}"}), 400

    # Validar fecha
    try:
        fecha_compra = datetime.strptime(data['fecha_compra'], "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "Formato de fecha inválido (use YYYY-MM-DD)"}), 400

    # 🧮 Generar código automáticamente (siguiente número disponible)
    ultimo_equipo = Equipo.query.order_by(Equipo.id.desc()).first()
    nuevo_codigo = str(int(ultimo_equipo.codigo) + 1) if ultimo_equipo and ultimo_equipo.codigo.isdigit() else "1"

    # 🧭 Calcular próximo mantenimiento
    periodo = data['periodo_mantenimiento'].lower()
    proximo_mantenimiento = None
    if "proximo_mantenimiento" in data and data.get("proximo_mantenimiento"):
        try:
            proximo_mantenimiento = datetime.strptime(data["proximo_mantenimiento"], "%Y-%m-%d").date()
        except Exception:
        # si el frontend envía algo inválido, lo ignoramos (no abortamos)
            proximo_mantenimiento = None

    nuevo_equipo = Equipo(
    codigo=data['codigo'],
    nombre=data['nombre'],
    marca=data['marca'],
    modelo=data['modelo'],
    fecha_compra=fecha_compra,
    periodo_mantenimiento=data['periodo_mantenimiento'],
    estado=data['estado'],
    imagen_url=data.get('imagen_url'),
    proximo_mantenimiento=proximo_mantenimiento,
    ultimo_mantenimiento=fecha_compra  # Asumimos que el último mantenimiento es la fecha de compra inicialmente
)

    db.session.add(nuevo_equipo)
    db.session.commit()

    return jsonify({"mensaje": "✅ Equipo agregado correctamente", "codigo": nuevo_equipo.codigo}), 201



# Editar equipo existente
@routes.route('/equipos/<int:id>', methods=['PUT'])
def editar_equipo(id):
    data = request.get_json() or {}
    equipo = Equipo.query.get(id)

    if not equipo:
        return jsonify({"error": "Equipo no encontrado"}), 404

    # Actualizar solo los campos enviados
    if "nombre" in data:
        equipo.nombre = data["nombre"]
    if "marca" in data:
        equipo.marca = data["marca"]
    if "modelo" in data:
        equipo.modelo = data["modelo"]
    if "fecha_compra" in data:
        try:
            equipo.fecha_compra = datetime.strptime(data["fecha_compra"], "%Y-%m-%d").date()
        except Exception:
            return jsonify({"error": "Formato de fecha inválido (use YYYY-MM-DD)"}), 400
    if "periodo_mantenimiento" in data:
        equipo.periodo_mantenimiento = data["periodo_mantenimiento"]
    if "estado" in data:
        equipo.estado = data["estado"]
    if "imagen_url" in data:  
        equipo.imagen_url = data["imagen_url"]
    try:
        from dateutil.relativedelta import relativedelta
        if equipo.fecha_compra and equipo.periodo_mantenimiento:
            meses = int(equipo.periodo_mantenimiento)
            equipo.proximo_mantenimiento = equipo.fecha_compra + relativedelta(months=meses)
    except ValueError:
        equipo.proximo_mantenimiento = None

    db.session.commit()
    return jsonify({"mensaje": "✅ Equipo actualizado correctamente"})


# Eliminar equipo (y sus mantenimientos asociados)
@routes.route('/equipos/<int:id>', methods=['DELETE'])
def eliminar_equipo(id):
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({"error": "Equipo no encontrado"}), 404

    # Eliminar mantenimientos asociados para evitar error de clave foránea
    for m in equipo.mantenimientos:
        db.session.delete(m)

    db.session.delete(equipo)
    db.session.commit()
    return jsonify({"mensaje": "🗑️ Equipo y mantenimientos asociados eliminados correctamente"}), 200


# Obtener detalle de un equipo
@routes.route('/equipos/<int:id>', methods=['GET'])
def detalle_equipo(id):
    e = Equipo.query.get(id)
    if not e:
        return jsonify({"error": "Equipo no encontrado"}), 404

    return jsonify({
        "id": e.id,
        "codigo": e.codigo,
        "nombre": e.nombre,
        "marca": e.marca,
        "modelo": e.modelo,
        "fecha_compra": str(e.fecha_compra) if e.fecha_compra else None,
        "periodo_mantenimiento": e.periodo_mantenimiento,
        "estado": e.estado,
        "imagen_url": e.imagen_url,
        "proximo_mantenimiento": str(e.proximo_mantenimiento) if e.proximo_mantenimiento else None,
        "ultimo_mantenimiento": str(e.ultimo_mantenimiento) if e.ultimo_mantenimiento else None
    })


# Listar todos los equipos
@routes.route('/equipos', methods=['GET'])
def obtener_equipos():
    equipos = Equipo.query.all()
    resultado = []
    for e in equipos:
        resultado.append({
            "id": e.id,
            "codigo": e.codigo,
            "nombre": e.nombre,
            "marca": e.marca,
            "modelo": e.modelo,
            "fecha_compra": str(e.fecha_compra),
            "periodo_mantenimiento": e.periodo_mantenimiento,
            "estado": e.estado,
            "imagen_url": e.imagen_url,
            "proximo_mantenimiento": str(e.proximo_mantenimiento) if e.proximo_mantenimiento else None,
            "ultimo_mantenimiento": str(e.ultimo_mantenimiento) if e.ultimo_mantenimiento else None
        })
    return jsonify(resultado)


# ============================================================
# 🟣 MANTENIMIENTOS
# ============================================================

# Crear mantenimiento
@routes.route('/mantenimientos', methods=['POST'])
def agregar_mantenimiento():
    data = request.get_json() or {}

    required = ['equipo_id', 'tipo', 'fecha']
    for key in required:
        if key not in data:
            return jsonify({"error": f"Falta campo requerido: {key}"}), 400

    # Verificar que el equipo exista
    equipo = Equipo.query.get(data['equipo_id'])
    if not equipo:
        return jsonify({"error": "Equipo no encontrado"}), 404

    # Validar fecha
    try:
        fecha_obj = datetime.strptime(data['fecha'], "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "Formato de fecha inválido (use YYYY-MM-DD)"}), 400

    nuevo = Mantenimiento(
        tipo=data.get('tipo'),
        fecha=fecha_obj,
        agente=data.get('agente'),
        descripcion=data.get('descripcion'),
        equipo_id=data.get('equipo_id')
    )

    db.session.add(nuevo)
    equipo.ultimo_mantenimiento = nuevo.fecha 
    try:
        meses = int(equipo.periodo_mantenimiento)
        equipo.proximo_mantenimiento = nuevo.fecha + relativedelta(months=meses)
    except ValueError:
        equipo.proximo_mantenimiento = None
    db.session.commit()

    return jsonify({"mensaje": "✅ Mantenimiento registrado correctamente", "id": nuevo.id}), 201


# Listar mantenimientos (con opción de filtrar por equipo)
@routes.route('/mantenimientos', methods=['GET'])
def listar_mantenimientos():
    equipo_id = request.args.get('equipo_id')
    query = Mantenimiento.query

    if equipo_id:
        query = query.filter_by(equipo_id=equipo_id)

    mantenimientos = query.order_by(Mantenimiento.fecha.desc()).all()
    resultado = []
    for m in mantenimientos:
        resultado.append({
            "id": m.id,
            "tipo": m.tipo,
            "fecha": str(m.fecha),
            "agente": m.agente,
            "descripcion": m.descripcion,
            "equipo_id": m.equipo_id,
            "equipo_nombre": m.equipo.nombre if m.equipo else None
        })

    return jsonify(resultado)


# Detalle de mantenimiento
@routes.route('/mantenimientos/<int:id>', methods=['GET'])
def detalle_mantenimiento(id):
    m = Mantenimiento.query.get(id)
    if not m:
        return jsonify({"error": "Mantenimiento no encontrado"}), 404

    return jsonify({
        "id": m.id,
        "tipo": m.tipo,
        "fecha": str(m.fecha),
        "agente": m.agente,
        "descripcion": m.descripcion,
        "equipo_id": m.equipo_id,
        "equipo_nombre": m.equipo.nombre if m.equipo else None
    })


# Editar mantenimiento
@routes.route('/mantenimientos/<int:id>', methods=['PUT'])
def editar_mantenimiento(id):
    data = request.get_json() or {}
    mantenimiento = Mantenimiento.query.get(id)
    if not mantenimiento:
        return jsonify({"error": "Mantenimiento no encontrado"}), 404

    if "tipo" in data:
        mantenimiento.tipo = data["tipo"]
    if "fecha" in data:
        try:
            mantenimiento.fecha = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
        except Exception:
            return jsonify({"error": "Formato de fecha inválido (use YYYY-MM-DD)"}), 400
    if "agente" in data:
        mantenimiento.agente = data["agente"]
    if "descripcion" in data:
        mantenimiento.descripcion = data["descripcion"]
    if "equipo_id" in data:
        equipo = Equipo.query.get(data["equipo_id"])
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        mantenimiento.equipo_id = data["equipo_id"]

    db.session.commit()
    return jsonify({"mensaje": "✅ Mantenimiento actualizado correctamente"})


# Eliminar mantenimiento
@routes.route('/mantenimientos/<int:id>', methods=['DELETE'])
def eliminar_mantenimiento(id):
    m = Mantenimiento.query.get(id)
    if not m:
        return jsonify({"error": "Mantenimiento no encontrado"}), 404

    db.session.delete(m)
    db.session.commit()
    return jsonify({"mensaje": "🗑️ Mantenimiento eliminado correctamente"}), 200
