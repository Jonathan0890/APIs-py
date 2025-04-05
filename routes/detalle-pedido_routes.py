from flask import Blueprint, request, jsonify
from config import mysql

detalle_bp = Blueprint('detalle_bp', __name__)

# Obtener todos los detalles de pedido
@detalle_bp.route('/', methods=['GET'])
def get_detalles_pedido():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detalles_pedido")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    detalles_pedido = [dict(zip(column_names, row)) for row in rows]
    return jsonify(detalles_pedido), 200

# Obtener un detalle de pedido específico
@detalle_bp.route('/<int:id_detalle>', methods=['GET'])
def get_detalle(id_detalle):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detalles_pedido WHERE id_detalle = %s", (id_detalle,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        detalle = dict(zip(column_names, row))
        return jsonify(detalle), 200
    return jsonify({'error': 'Detalle not found'}), 404

# Crear un nuevo detalle de pedido
@detalle_bp.route('/', methods=['POST'])
def create_detalle():
    data = request.json
    id_pedido = data.get('id_pedido')
    id_producto = data.get('id_producto')
    cantidad = data.get('cantidad')
    precio_unitario = data.get('precio_unitario')

    if not id_pedido or not id_producto or not cantidad or not precio_unitario:
        return jsonify({'error': 'All fields (id_pedido, id_producto, cantidad, precio_unitario) are required'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario)
        VALUES (%s, %s, %s, %s)
    """, (id_pedido, id_producto, cantidad, precio_unitario))
    conn.commit()
    return jsonify({'message': 'Detalle created!'}), 201

# Actualizar un detalle de pedido existente
@detalle_bp.route('/<int:id_detalle>', methods=['PUT'])
def update_detalle(id_detalle):
    data = request.json
    id_pedido = data.get('id_pedido')
    id_producto = data.get('id_producto')
    cantidad = data.get('cantidad')
    precio_unitario = data.get('precio_unitario')

    if not id_pedido or not id_producto or not cantidad or not precio_unitario:
        return jsonify({'error': 'All fields (id_pedido, id_producto, cantidad, precio_unitario) are required'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE detalles_pedido
        SET id_pedido = %s, id_producto = %s, cantidad = %s, precio_unitario = %s
        WHERE id_detalle = %s
    """, (id_pedido, id_producto, cantidad, precio_unitario, id_detalle))
    conn.commit()
    return jsonify({'message': 'Detalle updated!'}), 200

# Eliminar un detalle de pedido
@detalle_bp.route('/<int:id_detalle>', methods=['DELETE'])
def delete_detalle(id_detalle):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM detalles_pedido WHERE id_detalle = %s", (id_detalle,))
    conn.commit()
    return jsonify({'message': 'Detalle deleted!'}), 200
