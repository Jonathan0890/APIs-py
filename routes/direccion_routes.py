from flask import Blueprint, request, jsonify
from service.service_direccion import (
    get_all_direcciones, get_direccion_by_id,
    create_direccion, update_direccion, delete_direccion
)

direccion_bp = Blueprint('direccion_bp', __name__)

@direccion_bp.route('/', methods=['GET'])
def get_direcciones():
    return jsonify(get_all_direcciones()), 200

@direccion_bp.route('/<int:id_direccion>', methods=['GET'])
def get_direccion(id_direccion):
    direccion = get_direccion_by_id(id_direccion)
    if direccion:
        return jsonify(direccion), 200
    return jsonify({'error': 'Direccion not found'}), 404

@direccion_bp.route('/', methods=['POST'])
def create():
    data = request.json
    if not data.get('id_cliente') or not data.get('codigo_postal'):
        return jsonify({'error': 'id_cliente and codigo_postal are required fields'}), 400
    create_direccion(data)
    return jsonify({'message': 'Direccion creada'}), 201

@direccion_bp.route('/<int:id_direccion>', methods=['PUT'])
def update(id_direccion):
    data = request.json
    if not data.get('id_cliente') or not data.get('codigo_postal'):
        return jsonify({'error': 'id_cliente and codigo_postal are required fields'}), 400
    update_direccion(id_direccion, data)
    return jsonify({'message': 'Direccion actualizada'}), 200

@direccion_bp.route('/<int:id_direccion>', methods=['DELETE'])
def delete(id_direccion):
    delete_direccion(id_direccion)
    return jsonify({'message': 'Direccion eliminada'}), 200
