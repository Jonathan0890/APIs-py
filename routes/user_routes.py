from flask import Blueprint, request, jsonify
from config import mysql

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET'])
def get_users():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")  # Cambio a la tabla 'users'
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    users = [dict(zip(column_names, row)) for row in rows]
    return jsonify(users), 200


@user_bp.route('/<int:id_cliente>', methods=['GET'])
def get_user(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))  # Cambio en columna
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        user = dict(zip(column_names, row))
        return jsonify(user), 200
    return jsonify({'error': 'user not found'}), 404


@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    nombre = data.get('nombre')
    contrasena = data.get('contrasena')
    email = data.get('email')
    direccion = data.get('direccion')
    ciudad = data.get('ciudad')
    estado = data.get('estado')
    pais = data.get('pais')
    

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
                INSERT INTO clientes (nombre, contrasena, email, direccion, ciudad, estado, pais) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""", (nombre, contrasena, email, direccion, ciudad, estado, pais))
    conn.commit()
    return jsonify({'message': 'User created!'}), 201  



@user_bp.route('/<int:id_cliente>', methods=['PUT'])
def update_user(id_cliente):
    data = request.json
    nombre = data.get('nombre')
    contrasena = data.get('contrasena','' )
    email = data.get('email','' )
    direccion = data.get('direccion','' )
    ciudad = data.get('ciudad', '')
    estado = data.get('estado','' )
    pais = data.get('pais','' )
    

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
                UPDATE clientes
                SET nombre=%s, contrasena=%s, email=%s, direccion?=%s, ciudad=%s, estado=%s, pais=%s) 
                WHERE id_cliente=%s
                """, (nombre, contrasena, email, direccion, ciudad, estado, pais))
    conn.commit()
    return jsonify({'message': 'User updated!'}), 200  

@user_bp.route('/<int:id_cliente>', methods=['DELETE'])
def delete_user(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    return jsonify({'message': 'User deleted!'}), 200
