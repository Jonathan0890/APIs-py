from flask import Blueprint, request, jsonify
from config import mysql

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/', methods=['GET'])
def get_Admins():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administradores")  # Cambio a la tabla 'administrador'
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    Admins = [dict(zip(column_names, row)) for row in rows]
    return jsonify(Admins), 200


@admin_bp.route('/<int:id_administrador>', methods=['GET'])
def get_Admin(id_administrador):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administradores WHERE id_administrador = %s", (id_administrador,))  # Cambio en columna
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        Admin = dict(zip(column_names, row))
        return jsonify(Admin), 200
    return jsonify({'error': 'Admin not found'}), 404


@admin_bp.route('/', methods=['POST'])
def create_Admin():
    data = request.json
    nombre = data.get('nombre')
    email = data.get('email', '')  # Valor por defecto si no se proporciona
    contrasena = data.get('contrasena')

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO administradores (nombre, email, contrasena)
        VALUES (%s, %s, %s, %s)
    """, (nombre, email, contrasena))
    conn.commit()
    return jsonify({'message': 'Admin created!'}), 201


@admin_bp.route('/<int:id_administrador>', methods=['PUT'])
def update_Admin(id_administrador):
    data = request.json
    nombre = data.get('nombre')
    email = data.get('email', '')
    contrasena = data.get('contrasena')

    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE administradores
        SET nombre = %s, email = %s, contrasena = %s
        WHERE id_administrador = %s
    """, (nombre, email, contrasena, id_administrador))
    conn.commit()
    return jsonify({'message': 'Admin updated!'}), 200


@admin_bp.route('/<int:id_administrador>', methods=['DELETE'])
def delete_Admin(id_administrador):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM administradores WHERE id_administrador = %s", (id_administrador,))
    conn.commit()
    return jsonify({'message': 'Admin deleted!'}), 200
