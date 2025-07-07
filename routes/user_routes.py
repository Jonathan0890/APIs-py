from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from service.service_user import (
    get_all_users, get_user_by_id,
    create_user, update_user,
    delete_user, login_user
)

user_bp = Blueprint('user_bp', __name__)
logger = logging.getLogger(__name__)

# GET: Obtener todos los usuarios (restringido)
@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    try:
        users = get_all_users()
        return jsonify({"success": True, "data": users}), 200
    except Exception as e:
        logger.error(f"Error en get_users: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# GET: Obtener usuario por ID
@user_bp.route('/<int:id_cliente>', methods=['GET'])
@jwt_required()
def get_user(id_cliente):
    try:
        user = get_user_by_id(id_cliente)
        if user:
            return jsonify({"success": True, "data": user}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en get_user {id_cliente}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# POST: Crear nuevo usuario
@user_bp.route('/', methods=['POST'])
def create_user_route():
    data = request.json
    required_fields = ['nombre', 'contrasena', 'email']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"success": False, "message": "Faltan campos requeridos"}), 400
    try:
        user_id = create_user(data)
        return jsonify({"success": True, "message": "Usuario creado correctamente", "id": user_id}), 201
    except Exception as e:
        logger.error(f"Error en create_user: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# POST: Login de usuario
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('contrasena')

    if not email or not password:
        return jsonify({"success": False, "message": "Email y contraseña requeridos"}), 400

    result = login_user(email, password)
    if result:
        return jsonify({
            "success": True,
            "token": result['token'],
            "user": result['user']
        }), 200
    return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

# PUT: Actualizar usuario
@user_bp.route('/<int:id_cliente>', methods=['PUT'])
@jwt_required()
def update_user_route(id_cliente):
    data = request.json
    try:
        updated = update_user(id_cliente, data)
        if updated:
            return jsonify({"success": True, "message": "Usuario actualizado correctamente"}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en update_user {id_cliente}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# DELETE: Eliminar usuario
@user_bp.route('/<int:id_cliente>', methods=['DELETE'])
@jwt_required()
def delete_user_route(id_cliente):
    try:
        deleted = delete_user(id_cliente)
        if deleted:
            return jsonify({"success": True, "message": "Usuario eliminado correctamente"}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en delete_user {id_cliente}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
