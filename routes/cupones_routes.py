from flask import Blueprint, request, jsonify
from service.service_cupones import (
    obtener_todos_cupones,
    crear_cupon,
    validar_cupon,
    eliminar_cupon,
    registrar_uso_cupon
)

cupon_bp = Blueprint('cupon_bp', __name__)

# Obtener todos los cupones
@cupon_bp.route('/', methods=['GET'])
def list_cupones():
    try:
        cupones = obtener_todos_cupones()
        return jsonify({
            "success": True,
            "data": cupones,
            "count": len(cupones)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Crear un nuevo cupón
@cupon_bp.route('/', methods=['POST'])
def add_cupon():
    data = request.json
    codigo = data.get('codigo')
    descuento = data.get('descuento')
    valido_hasta = data.get('valido_hasta')

    if not codigo or not descuento or not valido_hasta:
        return jsonify({"success": False, "message": "Todos los campos son obligatorios"}), 400

    try:
        crear_cupon(codigo, descuento, valido_hasta)
        return jsonify({"success": True, "message": "Cupón creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Validar un cupón
@cupon_bp.route('/validar/<string:codigo>', methods=['GET'])
def validar(codigo):
    try:
        cupon = validar_cupon(codigo)
        if cupon:
            return jsonify({"success": True, "data": cupon}), 200
        return jsonify({"success": False, "message": "Cupón inválido o expirado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Eliminar un cupón
@cupon_bp.route('/<int:id_cupon>', methods=['DELETE'])
def remove_cupon(id_cupon):
    try:
        eliminar_cupon(id_cupon)
        return jsonify({"success": True, "message": "Cupón eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
