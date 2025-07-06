from flask import Blueprint, request, jsonify
from service.service_products import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)
import logging

product_bp = Blueprint('product_bp', __name__)
logger = logging.getLogger(__name__)

@product_bp.route('/', methods=['GET'])
def list_products():
    try:
        products = get_all_products()
        return jsonify({"success": True, "data": products}), 200
    except Exception as e:
        logger.error(f"Error en list_products: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = get_product_by_id(product_id)
        if product:
            return jsonify({"success": True, "data": product}), 200
        return jsonify({"success": False, "message": "Producto no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en get_product {product_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_bp.route('/', methods=['POST'])
def create_new_product():
    if not request.is_json:
        return jsonify({"success": False, "message": "Contenido debe ser JSON"}), 400

    data = request.get_json()
    try:
        product_id = create_product(data)
        product = get_product_by_id(product_id)
        return jsonify({
            "success": True,
            "message": "Producto creado",
            "data": product
        }), 201
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error en create_new_product: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
def modify_product(product_id):
    if not request.is_json:
        return jsonify({"success": False, "message": "Contenido debe ser JSON"}), 400

    data = request.get_json()
    try:
        updated = update_product(product_id, data)
        if updated:
            product = get_product_by_id(product_id)
            return jsonify({
                "success": True,
                "message": "Producto actualizado",
                "data": product
            }), 200
        return jsonify({"success": False, "message": "Producto no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en modify_product {product_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def remove_product(product_id):
    try:
        deleted = delete_product(product_id)
        if deleted:
            return jsonify({"success": True, "message": "Producto eliminado"}), 200
        return jsonify({"success": False, "message": "Producto no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error en remove_product {product_id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
