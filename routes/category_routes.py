from flask import Blueprint, request, jsonify
from config import mysql

category_bp = Blueprint('category_bp', __name__)

@category_bp.route('/', methods=['GET'])
def get_categories():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categorias")  # Cambio a la tabla 'categorias'
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    categories = [dict(zip(column_names, row)) for row in rows]
    return jsonify(categories), 200

@category_bp.route('/<int:id_categoria>', methods=['GET'])
def get_category(id_categoria):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categorias WHERE id_categoria = %s", (id_categoria,))  # Cambio en columna
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        category = dict(zip(column_names, row))
        return jsonify(category), 200
    return jsonify({'error': 'Category not found'}), 404

@category_bp.route('/', methods=['POST'])
def create_category():
    data = request.json
    nombre = data.get('nombre')  # Cambio de 'name' a 'nombre'

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO categorias (nombre)
        VALUES (%s)
    """, (nombre,))
    conn.commit()
    return jsonify({'message': 'Category created!'}), 201

@category_bp.route('/<int:id_categoria>', methods=['PUT'])
def update_category(id_categoria):
    data = request.json
    nombre = data.get('nombre')  # Cambio de 'name' a 'nombre'

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE categorias
        SET nombre = %s
        WHERE id_categoria = %s
    """, (nombre, id_categoria))
    conn.commit()
    return jsonify({'message': 'Category updated!'}), 200

@category_bp.route('/<int:id_categoria>', methods=['DELETE'])
def delete_category(id_categoria):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (id_categoria,))
    conn.commit()
    return jsonify({'message': 'Category deleted!'}), 200
