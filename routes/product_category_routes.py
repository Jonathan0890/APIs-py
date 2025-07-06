from flask import Blueprint, request, jsonify
from service.service_product_category import (
    get_all_product_categories,
    get_product_category_by_id,
    create_product_category,
    update_product_category,
    delete_product_category
)
import logging

product_category_bp = Blueprint('product_category_bp', __name__)
logger = logging.getLogger(__name__)

@product_category_bp.route('/', methods=['GET'])
def list_product_categories():
    try:
        data = get_all_product_categories()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error(f"Error en list_product_categories: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_category_bp.route('/<int:id>', methods=['GET'])
def get_product_category(id):
    try:
        data = get_product_category_by_id(id)
        if data:
            return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "message": "Relación no encontrada"}), 404
    except Exception as e:
        logger.error(f"Error en get_product_category {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_category_bp.route('/', methods=['POST'])
def add_product_category():
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400
    data = request.get_json()
    try:
        new_id = create_product_category(data)
        created = get_product_category_by_id(new_id)
        return jsonify({"success": True, "message": "Relación creada", "data": created}), 201
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error en add_product_category: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_category_bp.route('/<int:id>', methods=['PUT'])
def modify_product_category(id):
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400
    data = request.get_json()
    try:
        updated = update_product_category(id, data)
        if updated:
            refreshed = get_product_category_by_id(id)
            return jsonify({"success": True, "message": "Relación actualizada", "data": refreshed}), 200
        return jsonify({"success": False, "message": "Relación no encontrada"}), 404
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error en modify_product_category {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_category_bp.route('/<int:id>', methods=['DELETE'])
def remove_product_category(id):
    try:
        deleted = delete_product_category(id)
        if deleted:
            return jsonify({"success": True, "message": "Relación eliminada"}), 200
        return jsonify({"success": False, "message": "Relación no encontrada"}), 404
    except Exception as e:
        logger.error(f"Error en remove_product_category {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
