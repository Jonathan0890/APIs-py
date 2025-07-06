from flask import Blueprint, request, jsonify
from service.service_pago import *
import logging

pago_bp = Blueprint('pago_bp', __name__)
logger = logging.getLogger(__name__)

@pago_bp.route('/', methods=['GET'])
def get_all():
    pagos = get_all_pagos()
    return jsonify({"success": True, "data": pagos}), 200

@pago_bp.route('/<int:id_pago>', methods=['GET'])
def get_by_id(id_pago):
    pago = get_pago_by_id(id_pago)
    if pago:
        return jsonify({"success": True, "data": pago}), 200
    return jsonify({"success": False, "message": "Pago no encontrado"}), 404

@pago_bp.route('/', methods=['POST'])
def create():
    data = request.json
    if not data.get('id_pedido') or not data.get('metodo_pago'):
        return jsonify({"success": False, "message": "id_pedido y metodo_pago son requeridos"}), 400

    if data['metodo_pago'] not in ['tarjeta', 'paypal', 'transferencia']:
        return jsonify({"success": False, "message": "metodo_pago inválido"}), 400

    if data.get('estado_pago') and data['estado_pago'] not in ['pendiente', 'completado', 'fallido']:
        return jsonify({"success": False, "message": "estado_pago inválido"}), 400

    try:
        new_id = create_pago(data)
        return jsonify({"success": True, "message": "Pago creado", "id": new_id}), 201
    except Exception as e:
        logger.error(f"Error creando pago: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@pago_bp.route('/<int:id_pago>', methods=['PUT'])
def update(id_pago):
    data = request.json
    updated = update_pago(id_pago, data)
    if updated:
        return jsonify({"success": True, "message": "Pago actualizado"}), 200
    return jsonify({"success": False, "message": "No se actualizó ningún campo"}), 400

@pago_bp.route('/<int:id_pago>', methods=['DELETE'])
def delete(id_pago):
    deleted = delete_pago(id_pago)
    if deleted:
        return jsonify({"success": True, "message": "Pago eliminado"}), 200
    return jsonify({"success": False, "message": "Pago no encontrado"}), 404
