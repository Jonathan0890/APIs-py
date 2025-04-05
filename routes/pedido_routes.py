from flask import Blueprint, request, jsonify
from config import mysql

pedido_bp = Blueprint('pedido_bp', __name__)

@pedido_bp.route('/', methods=['GET'])
def get_pedidos():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos")  # Consulta a la tabla 'pedidos'
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    pedidos = [dict(zip(column_names, row)) for row in rows]
    return jsonify(pedidos), 200


@pedido_bp.route('/<int:id_pedido>', methods=['GET'])
def get_pedido(id_pedido):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE id_pedido = %s", (id_pedido,))  # Usar columna correcta
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        pedido = dict(zip(column_names, row))
        return jsonify(pedido), 200
    return jsonify({'error': 'Pedido not found'}), 404


@pedido_bp.route('/', methods=['POST'])
def create_pedido():
    data = request.json
    id_cliente = data.get('id_cliente')
    total = data.get('total')

    if not id_cliente or not total:
        return jsonify({'error': 'id_cliente and total are required fields'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pedidos (id_cliente, total)
        VALUES (%s, %s)
    """, (id_cliente, total))
    conn.commit()
    return jsonify({'message': 'Pedido created!'}), 201


@pedido_bp.route('/<int:id_pedido>', methods=['PUT'])
def update_pedido(id_pedido):
    data = request.json
    id_cliente = data.get('id_cliente')
    total = data.get('total')

    if not id_cliente or not total:
        return jsonify({'error': 'id_cliente and total are required fields'}), 400

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pedidos 
        SET id_cliente = %s, total = %s
        WHERE id_pedido = %s
    """, (id_cliente, total, id_pedido))
    conn.commit()
    return jsonify({'message': 'Pedido updated!'}), 200


@pedido_bp.route('/<int:id_pedido>', methods=['DELETE'])
def delete_pedido(id_pedido):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id_pedido,))
    conn.commit()
    return jsonify({'message': 'Pedido deleted!'}), 200
