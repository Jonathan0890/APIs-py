from flask import Blueprint, request, jsonify
from config import mysql
from datetime import datetime

pago_bp = Blueprint('pago_bp', __name__)

# Obtener todos los pagos
@pago_bp.route('/', methods=['GET'])
def get_pagos():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pagos")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    pagos = [dict(zip(column_names, row)) for row in rows]
    return jsonify(pagos), 200

# Obtener un pago específico
@pago_bp.route('/<int:id_pago>', methods=['GET'])
def get_pago(id_pago):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pagos WHERE id_pago = %s", (id_pago,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        pago = dict(zip(column_names, row))
        return jsonify(pago), 200
    return jsonify({'error': 'Pago not found'}), 404

# Crear un nuevo pago
@pago_bp.route('/', methods=['POST'])
def create_pago():
    data = request.json
    id_pedido = data.get('id_pedido')
    metodo_pago = data.get('metodo_pago')
    estado_pago = data.get('estado_pago', 'pendiente')  # Valor por defecto
    fecha_pago = datetime.now()  # Se asigna la fecha actual

    if not id_pedido or not metodo_pago:
        return jsonify({'error': 'id_pedido and metodo_pago are required fields'}), 400

    if metodo_pago not in ['tarjeta', 'paypal', 'transferencia']:
        return jsonify({'error': 'Invalid metodo_pago. Must be tarjeta, paypal, or transferencia'}), 400

    if estado_pago not in ['pendiente', 'completado', 'fallido']:
        return jsonify({'error': 'Invalid estado_pago. Must be pendiente, completado, or fallido'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pagos (id_pedido, metodo_pago, estado_pago, fecha_pago)
        VALUES (%s, %s, %s, %s)
    """, (id_pedido, metodo_pago, estado_pago, fecha_pago))
    conn.commit()
    return jsonify({'message': 'Pago created!'}), 201

# Actualizar un pago existente
@pago_bp.route('/<int:id_pago>', methods=['PUT'])
def update_pago(id_pago):
    data = request.json
    metodo_pago = data.get('metodo_pago')
    estado_pago = data.get('estado_pago')

    if metodo_pago and metodo_pago not in ['tarjeta', 'paypal', 'transferencia']:
        return jsonify({'error': 'Invalid metodo_pago. Must be tarjeta, paypal, or transferencia'}), 400

    if estado_pago and estado_pago not in ['pendiente', 'completado', 'fallido']:
        return jsonify({'error': 'Invalid estado_pago. Must be pendiente, completado, or fallido'}), 400

    # Si no se especifica el estado, no cambiamos la fecha
    fecha_pago = datetime.now() if estado_pago else None

    conn = mysql.connection
    cursor = conn.cursor()
    update_fields = []
    update_values = []

    if metodo_pago:
        update_fields.append("metodo_pago = %s")
        update_values.append(metodo_pago)
    if estado_pago:
        update_fields.append("estado_pago = %s")
        update_values.append(estado_pago)
    if fecha_pago:
        update_fields.append("fecha_pago = %s")
        update_values.append(fecha_pago)

    update_values.append(id_pago)
    cursor.execute(f"""
        UPDATE pagos
        SET {', '.join(update_fields)}
        WHERE id_pago = %s
    """, update_values)
    conn.commit()
    return jsonify({'message': 'Pago updated!'}), 200

# Eliminar un pago
@pago_bp.route('/<int:id_pago>', methods=['DELETE'])
def delete_pago(id_pago):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pagos WHERE id_pago = %s", (id_pago,))
    conn.commit()
    return jsonify({'message': 'Pago deleted!'}), 200
