from flask import Blueprint, request, jsonify
from config import mysql

productos_categorias_bp = Blueprint('productos_categorias_bp', __name__)

# Obtener todas las relaciones entre productos y categorías
@productos_categorias_bp.route('/', methods=['GET'])
def get_productos_categorias():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pc.id_producto_categoria, pc.id_producto, p.nombre AS producto, 
            pc.id_categoria, c.nombre AS categoria
        FROM productos_categorias pc
        JOIN productos p ON pc.id_producto = p.id_producto
        JOIN categorias c ON pc.id_categoria = c.id_categoria
    """)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    productos_categorias = [dict(zip(column_names, row)) for row in rows]
    return jsonify(productos_categorias), 200

# Obtener una relación específica por ID
@productos_categorias_bp.route('/<int:id_producto_categoria>', methods=['GET'])
def get_producto_categoria(id_producto_categoria):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pc.id_producto_categoria, pc.id_producto, p.nombre AS producto, 
            pc.id_categoria, c.nombre AS categoria
        FROM productos_categorias pc
        JOIN productos p ON pc.id_producto = p.id_producto
        JOIN categorias c ON pc.id_categoria = c.id_categoria
        WHERE pc.id_producto_categoria = %s
    """, (id_producto_categoria,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        producto_categoria = dict(zip(column_names, row))
        return jsonify(producto_categoria), 200
    return jsonify({'error': 'producto_categoria not found'}), 404

# Crear una nueva relación entre producto y categoría
@productos_categorias_bp.route('/', methods=['POST'])
def create_producto_categoria():
    data = request.json
    id_producto = data.get('id_producto')
    id_categoria = data.get('id_categoria')

    if not id_producto or not id_categoria:
        return jsonify({'error': 'id_producto and id_categoria are required fields'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos_categorias (id_producto, id_categoria)
        VALUES (%s, %s)
    """, (id_producto, id_categoria))
    conn.commit()
    return jsonify({'message': 'producto_categoria created!'}), 201

# Actualizar una relación existente
@productos_categorias_bp.route('/<int:id_producto_categoria>', methods=['PUT'])
def update_producto_categoria(id_producto_categoria):
    data = request.json
    id_producto = data.get('id_producto')
    id_categoria = data.get('id_categoria')

    if not id_producto or not id_categoria:
        return jsonify({'error': 'id_producto and id_categoria are required fields'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos_categorias
        SET id_producto = %s, id_categoria = %s
        WHERE id_producto_categoria = %s
    """, (id_producto, id_categoria, id_producto_categoria))
    conn.commit()
    return jsonify({'message': 'producto_categoria updated!'}), 200

# Eliminar una relación entre producto y categoría
@productos_categorias_bp.route('/<int:id_producto_categoria>', methods=['DELETE'])
def delete_producto_categoria(id_producto_categoria):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos_categorias WHERE id_producto_categoria = %s", (id_producto_categoria,))
    conn.commit()
    return jsonify({'message': 'producto_categoria deleted!'}), 200
