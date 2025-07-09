from flask import Blueprint, request, jsonify
from utils.ia_helper import analizar_sentimiento_resena

resena_ia_bp = Blueprint('resena_ia_bp', __name__)

@resena_ia_bp.route('/analizar', methods=['POST'])
def analizar_resena():
    data = request.json
    comentario = data.get('comentario')

    if not comentario:
        return jsonify({'error': 'Se requiere un comentario'}), 400

    try:
        sentimiento = analizar_sentimiento_resena(comentario)
        return jsonify({'comentario': comentario, 'sentimiento': sentimiento}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
