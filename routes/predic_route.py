from flask import Blueprint, request, jsonify
from model.predictor import predecir_reservas, verificar_estado_modelo
import logging

logger = logging.getLogger(__name__)
predict_bp = Blueprint('predict_bp', __name__)

VALID_VALUES = {
    'dia_semana': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'tipo de unidad': ['twin_room', 'doble', 'suite', 'individual'],
    'motivo del viaje': ['ocio', 'trabajo'],
    'dispositivos': ['movil', 'ordenador'],
    'estado': ['confirmed', 'cancelled_by_guest']
}

@predict_bp.route('/status', methods=['GET'])
def estado_modelo():
    """Endpoint para verificar el estado del modelo"""
    try:
        estado = verificar_estado_modelo()
        return jsonify({
            'status': 'success',
            'estado_modelo': estado
        })
    except Exception as e:
        logger.error(f"Error al verificar estado: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@predict_bp.route('/', methods=['POST'])
def prediccion():
    try:
        datos = request.get_json()
        
        if not datos:
            raise ValueError("No se recibieron datos")
        
        # Validar campos requeridos
        required_fields = [
            'dia_semana', 'mes', 'anio', 'duracion(noches)', 'personas',
            'adulto', 'niños', 'anticipacion', 'tipo de unidad',
            'motivo del viaje', 'dispositivos', 'estado'
        ]
        
        missing_fields = [field for field in required_fields if field not in datos]
        if missing_fields:
            raise ValueError(f"Faltan campos: {', '.join(missing_fields)}")
        
        # Normalizar datos categóricos
        datos_normalizados = {}
        for field, value in datos.items():
            if field in VALID_VALUES:
                # Buscar valor válido (case-insensitive)
                normalized = next(
                    (v for v in VALID_VALUES[field] if str(value).lower() == v.lower()),
                    None
                )
                if normalized is None:
                    # Si no se encuentra, usar el primero como default
                    normalized = VALID_VALUES[field][0]
                    logger.warning(f"Valor inválido para {field}: {value}. Usando: {normalized}")
                
                datos_normalizados[field] = normalized
            else:
                # Para campos numéricos, convertir a número si es posible
                if field in ['mes', 'anio', 'duracion(noches)', 'personas', 'adulto', 'niños', 'anticipacion']:
                    try:
                        datos_normalizados[field] = float(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"El campo {field} debe ser numérico")
                else:
                    datos_normalizados[field] = value
        
        # Realizar predicción
        resultado = predecir_reservas(datos_normalizados)
        
        return jsonify({
            'prediccion_reservas': resultado,
            'mensaje': f"Predicción exitosa: {resultado} reservas",
            'status': 'success',
            'datos_procesados': datos_normalizados
        })
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'tipo_error': 'validacion'
        }), 400
        
    except RuntimeError as e:
        logger.error(f"Error de modelo: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'tipo_error': 'modelo'
        }), 503  # Service Unavailable
        
    except Exception as e:
        logger.error(f"Error inesperado en predicción: {str(e)}")
        return jsonify({
            'error': "Error interno del servidor",
            'status': 'error',
            'tipo_error': 'interno'
        }), 500