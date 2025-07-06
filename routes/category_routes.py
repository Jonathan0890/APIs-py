from flask import Blueprint, request, jsonify
from service.service_category import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)
import logging

category_bp = Blueprint('category_bp', __name__)
logger = logging.getLogger(__name__)

@category_bp.route('/', methods=['GET'])
def list_categories():
    try:
        categories = get_all_categories()
        return jsonify({"success": True, "data": categories}), 200
    except Exception as e:
        logger.error(f"Error en list_categories: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = get_category_by_id(category_id)
        if category:
            return jsonify({"success": True, "data": category}), 200
        return jsonify({"success": False, "message": "Categoría no encontrada"}), 404
    except Exception as e:
        logger.error(f"Error en get_category {category_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@category_bp.route('/', methods=['POST'])
def add_category():
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400
    data = request.get_json()
    try:
        new_id = create_category(data)
        new_category = get_category_by_id(new_id)
        return jsonify({"success": True, "message": "Categoría creada", "data": new_category}), 201
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error en add_category: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
def modify_category(category_id):
    if not request.is_json:
        return jsonify({"success": False, "message": "El contenido debe ser JSON"}), 400
    data = request.get_json()
    try:
        updated = update_category(category_id, data)
        if updated:
            updated_category = get_category_by_id(category_id)
            return jsonify({"success": True, "message": "Categoría actualizada", "data": updated_category}), 200
        return jsonify({"success": False, "message": "Categoría no encontrada"}), 404
    except Exception as e:
        logger.error(f"Error en modify_category {category_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
def remove_category(category_id):
    try:
        deleted = delete_category(category_id)
        if deleted:
            return jsonify({"success": True, "message": "Categoría eliminada"}), 200
        return jsonify({"success": False, "message": "Categoría no encontrada"}), 404
    except Exception as e:
        logger.error(f"Error en remove_category {category_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
