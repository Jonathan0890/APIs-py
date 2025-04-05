from flask import Blueprint, request, jsonify
from config import mysql
from datetime import datetime

resena_bp = Blueprint('resena_bp', __name__)

# Obtener todas las reseñas
@resena_bp.route('/', methods=['GET'])
def get_resenas():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resenas")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    resenas = [dict(zip(column_names, row)) for row in rows]
    return jsonify(resenas), 200

# Obtener una reseña específica
@resena_bp.route('/<int:id_resena>', methods=['GET'])
def get_resena(id_resena):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resenas WHERE id_resena = %s", (id_resena,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        resena = dict(zip(column_names, row))
        return jsonify(resena), 200
    return jsonify({'error': 'Reseña not found'}), 404

# Crear una nueva reseña
@resena_bp.route('/', methods=['POST'])
def create_resena():
    data = request.json
    id_producto = data.get('id_producto')
    id_cliente = data.get('id_cliente')
    calificacion = data.get('calificacion')
    comentario = data.get('comentario')
    fecha = datetime.now()  # Se asigna la fecha actual automáticamente

    # Validaciones
    if not id_producto or not id_cliente or not calificacion:
        return jsonify({'error': 'id_producto, id_cliente, and calificacion are required fields'}), 400

    if not (1 <= calificacion <= 5):
        return jsonify({'error': 'calificacion must be between 1 and 5'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resenas (id_producto, id_cliente, calificacion, comentario, fecha)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_producto, id_cliente, calificacion, comentario, fecha))
    conn.commit()
    return jsonify({'message': 'Reseña created!'}), 201

# Actualizar una reseña existente
@resena_bp.route('/<int:id_resena>', methods=['PUT'])
def update_resena(id_resena):
    data = request.json
    calificacion = data.get('calificacion')
    comentario = data.get('comentario')
    fecha = datetime.now()  # Actualizamos la fecha de modificación

    # Validaciones
    if calificacion and not (1 <= calificacion <= 5):
        return jsonify({'error': 'calificacion must be between 1 and 5'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    update_fields = []
    update_values = []

    if calificacion is not None:
        update_fields.append("calificacion = %s")
        update_values.append(calificacion)
    if comentario is not None:
        update_fields.append("comentario = %s")
        update_values.append(comentario)

    # Siempre actualizamos la fecha
    update_fields.append("fecha = %s")
    update_values.append(fecha)

    update_values.append(id_resena)
    cursor.execute(f"""
        UPDATE resenas
        SET {', '.join(update_fields)}
        WHERE id_resena = %s
    """, update_values)
    conn.commit()
    return jsonify({'message': 'Reseña updated!'}), 200

# Eliminar una reseña
@resena_bp.route('/<int:id_resena>', methods=['DELETE'])
def delete_resena(id_resena):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resenas WHERE id_resena = %s", (id_resena,))
    conn.commit()
    return jsonify({'message': 'Reseña deleted!'}), 200
