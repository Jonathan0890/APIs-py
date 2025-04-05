from flask import Blueprint, request, jsonify
from config import mysql

direccion_bp = Blueprint('direccion_bp', __name__)

# Obtener todas las direcciones
@direccion_bp.route('/', methods=['GET'])
def get_direcciones():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM direcciones")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    direcciones = [dict(zip(column_names, row)) for row in rows]
    return jsonify(direcciones), 200


# Obtener una dirección específica
@direccion_bp.route('/<int:id_direccion>', methods=['GET'])
def get_direccion(id_direccion):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM direcciones WHERE id_direccion = %s", (id_direccion,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        direccion = dict(zip(column_names, row))
        return jsonify(direccion), 200
    return jsonify({'error': 'Direccion not found'}), 404


# Crear una nueva dirección
@direccion_bp.route('/', methods=['POST'])
def create_direccion():
    data = request.json
    id_cliente = data.get('id_cliente')
    calle = data.get('calle')
    ciudad = data.get('ciudad')
    estado = data.get('estado')
    codigo_postal = data.get('codigo_postal')
    pais = data.get('pais')

    if not id_cliente or not codigo_postal:
        return jsonify({'error': 'id_cliente and codigo_postal are required fields'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO direcciones (id_cliente, calle, ciudad, estado, codigo_postal, pais)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_cliente, calle, ciudad, estado, codigo_postal, pais))
    conn.commit()
    return jsonify({'message': 'Direccion created!'}), 201


# Actualizar una dirección existente
@direccion_bp.route('/<int:id_direccion>', methods=['PUT'])
def update_direccion(id_direccion):
    data = request.json
    id_cliente = data.get('id_cliente')
    calle = data.get('calle')
    ciudad = data.get('ciudad')
    estado = data.get('estado')
    codigo_postal = data.get('codigo_postal')
    pais = data.get('pais')

    if not id_cliente or not codigo_postal:
        return jsonify({'error': 'id_cliente and codigo_postal are required fields'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE direcciones
        SET id_cliente = %s, calle = %s, ciudad = %s, estado = %s, codigo_postal = %s, pais = %s
        WHERE id_direccion = %s
    """, (id_cliente, calle, ciudad, estado, codigo_postal, pais, id_direccion))
    conn.commit()
    return jsonify({'message': 'Direccion updated!'}), 200


# Eliminar una dirección
@direccion_bp.route('/<int:id_direccion>', methods=['DELETE'])
def delete_direccion(id_direccion):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM direcciones WHERE id_direccion = %s", (id_direccion,))
    conn.commit()
    return jsonify({'message': 'Direccion deleted!'}), 200
