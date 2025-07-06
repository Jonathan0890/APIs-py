from flask import Blueprint, request, jsonify
from service.service_detalle_pedido import (
    get_all_detalles,
    get_detalle_by_id,
    create_detalle,
    update_detalle,
    delete_detalle
)
import logging

detalle_bp = Blueprint('detalle_bp', __name__)
logger = logging.getLogger(__name__)

# Obtener todos los detalles de pedido
@detalle_bp.route('/', methods=['GET'])
def list_detalles():
    try:
        detalles = get_all_detalles()
        return jsonify({
            "success": True,
            "data": detalles,
            "count": len(detalles)
        }), 200
    except Exception as e:
        logger.error(f"Error en list_detalles: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# Obtener un detalle de pedido específico
@detalle_bp.route('/<int:id>', methods=['GET'])
def get_detalle(id):
    try:
        detalle = get_detalle_by_id(id)
        if detalle:
            return jsonify({"success": True, "data": detalle}), 200
        return jsonify({"success": False, "message": "Detalle no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en get_detalle {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# Crear un nuevo detalle de pedido
@detalle_bp.route('/', methods=['POST'])
def add_detalle():
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400

    data = request.get_json()
    try:
        new_id = create_detalle(data)
        detalle = get_detalle_by_id(new_id)
        return jsonify({
            "success": True,
            "message": "Detalle creado exitosamente",
            "data": detalle
        }), 201
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error en add_detalle: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# Actualizar un detalle de pedido
@detalle_bp.route('/<int:id>', methods=['PUT'])
def modify_detalle(id):
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400

    data = request.get_json()
    try:
        updated = update_detalle(id, data)
        if updated:
            detalle = get_detalle_by_id(id)
            return jsonify({
                "success": True,
                "message": "Detalle actualizado exitosamente",
                "data": detalle
            }), 200
        return jsonify({"success": False, "message": "Detalle no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en modify_detalle {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# Eliminar un detalle de pedido
@detalle_bp.route('/<int:id>', methods=['DELETE'])
def remove_detalle(id):
    try:
        deleted = delete_detalle(id)
        if deleted:
            return jsonify({
                "success": True,
                "message": "Detalle eliminado correctamente"
            }), 200
        return jsonify({"success": False, "message": "Detalle no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en remove_detalle {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
