from flask import Blueprint, request, jsonify
from config import mysql

product_bp = Blueprint('product_bp', __name__)


@product_bp.route('/', methods=['GET'])
def get_products():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")  # Cambio a la tabla 'productos'
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    products = [dict(zip(column_names, row)) for row in rows]
    return jsonify(products), 200


@product_bp.route('/<int:id_producto>', methods=['GET'])
def get_product(id_producto):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))  # Cambio en columna
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        product = dict(zip(column_names, row))
        return jsonify(product), 200
    return jsonify({'error': 'Product not found'}), 404


@product_bp.route('/', methods=['POST'])
def create_product():
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')  # Valor por defecto si no se proporciona
    precio = data.get('precio')
    imagen = data.get('imagen', '')  # Valor por defecto si no se proporciona

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, descripcion, precio, imagen)
        VALUES (%s, %s, %s, %s)
    """, (nombre, descripcion, precio, imagen))
    conn.commit()
    return jsonify({'message': 'Product created!'}), 201


@product_bp.route('/<int:id_producto>', methods=['PUT'])
def update_product(id_producto):
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')
    precio = data.get('precio')
    imagen = data.get('imagen', '')

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos 
        SET nombre = %s, descripcion = %s, precio = %s, imagen = %s
        WHERE id_producto = %s
    """, (nombre, descripcion, precio, imagen, id_producto))
    conn.commit()
    return jsonify({'message': 'Product updated!'}), 200


@product_bp.route('/<int:id_producto>', methods=['DELETE'])
def delete_product(id_producto):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
    conn.commit()
    return jsonify({'message': 'Product deleted!'}), 200
