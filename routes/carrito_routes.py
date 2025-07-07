from flask import Blueprint, request, jsonify
from service.service_carrito import (
    get_carrito_by_cliente,
    add_producto_al_carrito,
    update_cantidad_carrito,
    delete_producto_carrito,
    vaciar_carrito_cliente
)

carrito_bp = Blueprint('carrito_bp', __name__)

@carrito_bp.route('/<int:id_cliente>', methods=['GET'])
def get_carrito(id_cliente):
    carrito = get_carrito_by_cliente(id_cliente)
    if not carrito:
        return jsonify({'message': 'El carrito está vacío o el cliente no existe'}), 404
    return jsonify(carrito), 200

@carrito_bp.route('/', methods=['POST'])
def add_to_carrito():
    data = request.json
    if not data.get('id_cliente') or not data.get('id_producto'):
        return jsonify({'error': 'id_cliente y id_producto son obligatorios'}), 400
    add_producto_al_carrito(data)
    return jsonify({'message': 'Producto agregado al carrito'}), 201

@carrito_bp.route('/<int:id_carrito>', methods=['PUT'])
def update_carrito(id_carrito):
    data = request.json
    cantidad = data.get('cantidad')
    if not cantidad or cantidad < 1:
        return jsonify({'error': 'La cantidad debe ser mayor o igual a 1'}), 400
    update_cantidad_carrito(id_carrito, cantidad)
    return jsonify({'message': 'Cantidad actualizada en el carrito'}), 200

@carrito_bp.route('/<int:id_carrito>', methods=['DELETE'])
def delete_from_carrito(id_carrito):
    delete_producto_carrito(id_carrito)
    return jsonify({'message': 'Producto eliminado del carrito'}), 200

@carrito_bp.route('/vaciar/<int:id_cliente>', methods=['DELETE'])
def empty_carrito(id_cliente):
    vaciar_carrito_cliente(id_cliente)
    return jsonify({'message': 'Carrito vaciado'}), 200
