from flask import Blueprint, request, jsonify
from service.service_pedido import (
    get_all_pedidos,
    get_pedido_by_id,
    create_pedido,
    update_pedido,
    delete_pedido
)
import logging

pedido_bp = Blueprint('pedido_bp', __name__)
logger = logging.getLogger(__name__)

@pedido_bp.route('/', methods=['GET'])
def list_pedidos():
    try:
        pedidos = get_all_pedidos()
        return jsonify({
            "success": True,
            "data": pedidos,
            "count": len(pedidos)
        }), 200
    except Exception as e:
        logger.error(f"Error en list_pedidos: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@pedido_bp.route('/<int:id>', methods=['GET'])
def get_pedido(id):
    try:
        pedido = get_pedido_by_id(id)
        if pedido:
            return jsonify({"success": True, "data": pedido}), 200
        return jsonify({"success": False, "message": "Pedido no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en get_pedido {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@pedido_bp.route('/', methods=['POST'])
def add_pedido():
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400

    data = request.get_json()
    try:
        new_id = create_pedido(data)
        created = get_pedido_by_id(new_id)
        return jsonify({
            "success": True,
            "message": "Pedido creado exitosamente",
            "data": created
        }), 201
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error en add_pedido: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@pedido_bp.route('/<int:id>', methods=['PUT'])
def modify_pedido(id):
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400

    data = request.get_json()
    try:
        updated = update_pedido(id, data)
        if updated:
            refreshed = get_pedido_by_id(id)
            return jsonify({
                "success": True,
                "message": "Pedido actualizado exitosamente",
                "data": refreshed
            }), 200
        return jsonify({"success": False, "message": "Pedido no encontrado"}), 404
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error en modify_pedido {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@pedido_bp.route('/<int:id>', methods=['DELETE'])
def remove_pedido(id):
    try:
        deleted = delete_pedido(id)
        if deleted:
            return jsonify({"success": True, "message": "Pedido eliminado correctamente"}), 200
        return jsonify({"success": False, "message": "Pedido no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en remove_pedido {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
