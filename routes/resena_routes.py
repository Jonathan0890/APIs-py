from flask import Blueprint, request, jsonify
from service.service_resena import (
    get_all_resenas, get_resena_by_id,
    create_resena, update_resena, delete_resena
)

resena_bp = Blueprint('resena_bp', __name__)

@resena_bp.route('/', methods=['GET'])
def get_resenas():
    return jsonify(get_all_resenas()), 200

@resena_bp.route('/<int:id_resena>', methods=['GET'])
def get_resena(id_resena):
    resena = get_resena_by_id(id_resena)
    if resena:
        return jsonify(resena), 200
    return jsonify({'error': 'Reseña not found'}), 404

@resena_bp.route('/', methods=['POST'])
def create():
    data = request.json
    if not data.get('id_producto') or not data.get('id_cliente') or not data.get('calificacion'):
        return jsonify({'error': 'id_producto, id_cliente y calificacion son obligatorios'}), 400
    if not (1 <= data['calificacion'] <= 5):
        return jsonify({'error': 'calificacion debe estar entre 1 y 5'}), 400
    create_resena(data)
    return jsonify({'message': 'Reseña creada'}), 201

@resena_bp.route('/<int:id_resena>', methods=['PUT'])
def update(id_resena):
    data = request.json
    if 'calificacion' in data and not (1 <= data['calificacion'] <= 5):
        return jsonify({'error': 'calificacion debe estar entre 1 y 5'}), 400
    update_resena(id_resena, data)
    return jsonify({'message': 'Reseña actualizada'}), 200

@resena_bp.route('/<int:id_resena>', methods=['DELETE'])
def delete(id_resena):
    delete_resena(id_resena)
    return jsonify({'message': 'Reseña eliminada'}), 200
