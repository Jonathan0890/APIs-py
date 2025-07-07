from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from service.service_auth import autenticar_usuario, generar_codigo_otp

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

# Login con email y contraseña
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    contrasena = data.get('contrasena')

    if not email or not contrasena:
        return jsonify({"success": False, "message": "Email y contraseña son obligatorios"}), 400

    auth_result = autenticar_usuario(email, contrasena)

    if auth_result:
        return jsonify({"success": True, "data": auth_result}), 200
    else:
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

# Generar y mostrar un código OTP
@auth_bp.route('/otp', methods=['GET'])
def obtener_otp():
    otp = generar_codigo_otp()
    return jsonify({"codigo_otp": otp}), 200

