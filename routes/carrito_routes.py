from flask import Blueprint, request, jsonify
from config import mysql
from datetime import datetime

carrito_bp = Blueprint('carrito_bp', __name__)

# Obtener todos los productos en el carrito de un cliente
@carrito_bp.route('/<int:id_cliente>', methods=['GET'])
def get_carrito(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id_carrito, c.id_producto, p.nombre, c.cantidad, c.fecha_agregado
        FROM carrito c
        JOIN productos p ON c.id_producto = p.id_producto
        WHERE c.id_cliente = %s
    """, (id_cliente,))
    rows = cursor.fetchall()
    if not rows:
        return jsonify({'message': 'El carrito está vacío o el cliente no existe'}), 404

    column_names = [desc[0] for desc in cursor.description]
    carrito = [dict(zip(column_names, row)) for row in rows]
    return jsonify(carrito), 200

# Agregar un producto al carrito
@carrito_bp.route('/', methods=['POST'])
def add_to_carrito():
    data = request.json
    id_cliente = data.get('id_cliente')
    id_producto = data.get('id_producto')
    cantidad = data.get('cantidad', 1)  # Por defecto, se agrega 1 unidad

    if not id_cliente or not id_producto:
        return jsonify({'error': 'id_cliente y id_producto son campos obligatorios'}), 400

    conn = mysql.connection
    cursor = conn.cursor()

    # Verificar si el producto ya está en el carrito
    cursor.execute("""
        SELECT cantidad FROM carrito 
        WHERE id_cliente = %s AND id_producto = %s
    """, (id_cliente, id_producto))
    row = cursor.fetchone()

    if row:
        # Si ya existe, actualizar la cantidad
        nueva_cantidad = row[0] + cantidad
        cursor.execute("""
            UPDATE carrito 
            SET cantidad = %s, fecha_agregado = %s 
            WHERE id_cliente = %s AND id_producto = %s
        """, (nueva_cantidad, datetime.now(), id_cliente, id_producto))
    else:
        # Si no existe, insertar un nuevo registro
        cursor.execute("""
            INSERT INTO carrito (id_cliente, id_producto, cantidad, fecha_agregado)
            VALUES (%s, %s, %s, %s)
        """, (id_cliente, id_producto, cantidad, datetime.now()))

    conn.commit()
    return jsonify({'message': 'Producto agregado al carrito'}), 201

# Actualizar la cantidad de un producto en el carrito
@carrito_bp.route('/<int:id_carrito>', methods=['PUT'])
def update_carrito(id_carrito):
    data = request.json
    cantidad = data.get('cantidad')

    if not cantidad or cantidad < 1:
        return jsonify({'error': 'La cantidad debe ser mayor o igual a 1'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE carrito
        SET cantidad = %s, fecha_agregado = %s
        WHERE id_carrito = %s
    """, (cantidad, datetime.now(), id_carrito))
    conn.commit()
    return jsonify({'message': 'Cantidad actualizada en el carrito'}), 200

# Eliminar un producto del carrito
@carrito_bp.route('/<int:id_carrito>', methods=['DELETE'])
def delete_from_carrito(id_carrito):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito WHERE id_carrito = %s", (id_carrito,))
    conn.commit()
    return jsonify({'message': 'Producto eliminado del carrito'}), 200

# Vaciar el carrito de un cliente
@carrito_bp.route('/vaciar/<int:id_cliente>', methods=['DELETE'])
def empty_carrito(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    return jsonify({'message': 'Carrito vaciado'}), 200
