from flask import Blueprint, request, jsonify
from config import mysql
import logging

user_bp = Blueprint('user_bp', __name__)
logger = logging.getLogger(__name__)

# GET: Obtener todos los usuarioss
@user_bp.route('/', methods=['GET'])
def get_users():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        users = [dict(zip(column_names, row)) for row in rows]
        return jsonify({"success": True, "data": users}), 200
    except Exception as e:
        logger.error(f"Error en get_users: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# GET: Obtener usuario por ID
@user_bp.route('/<int:id_cliente>', methods=['GET'])
def get_user(id_cliente):
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
        row = cursor.fetchone()
        if row:
            column_names = [desc[0] for desc in cursor.description]
            user = dict(zip(column_names, row))
            return jsonify({"success": True, "data": user}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en get_user {id_cliente}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# POST: Crear nuevo usuario
@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    required_fields = ['nombre', 'contrasena', 'email']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"success": False, "message": "Faltan campos requeridos"}), 400

    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre, contrasena, email, direccion, ciudad, estado, pais)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('nombre'),
            data.get('contrasena'),
            data.get('email'),
            data.get('direccion', ''),
            data.get('ciudad', ''),
            data.get('estado', ''),
            data.get('pais', '')
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Usuario creado correctamente"}), 201
    except Exception as e:
        logger.error(f"Error en create_user: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# PUT: Actualizar usuario
@user_bp.route('/<int:id_cliente>', methods=['PUT'])
def update_user(id_cliente):
    data = request.json
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes
            SET nombre=%s, contrasena=%s, email=%s, direccion=%s, ciudad=%s, estado=%s, pais=%s
            WHERE id_cliente=%s
        """, (
            data.get('nombre', ''),
            data.get('contrasena', ''),
            data.get('email', ''),
            data.get('direccion', ''),
            data.get('ciudad', ''),
            data.get('estado', ''),
            data.get('pais', ''),
            id_cliente
        ))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        return jsonify({"success": True, "message": "Usuario actualizado correctamente"}), 200
    except Exception as e:
        logger.error(f"Error en update_user {id_cliente}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# DELETE: Eliminar usuario
@user_bp.route('/<int:id_cliente>', methods=['DELETE'])
def delete_user(id_cliente):
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        return jsonify({"success": True, "message": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        logger.error(f"Error en delete_user {id_cliente}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
