from flask import Blueprint, request, jsonify
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear el Blueprint
predict_bp = Blueprint('predict_bp', __name__)

# Valores válidos para validación de entrada
VALID_VALUES = {
    'dia_semana': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    'tipo de unidad': ['twin_room', 'doble', 'suite', 'individual'],
    'motivo del viaje': ['ocio', 'trabajo'],
    'dispositivos': ['movil', 'ordenador'],
    'estado': ['confirmed', 'cancelled_by_guest']
}

# ---------- Endpoints ----------

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


@predict_bp.route('/diagnostico', methods=['GET'])
def diagnostico_modelo():
    """Endpoint para diagnóstico detallado del modelo"""
    try:
        diagnostico = diagnosticar_modelo()
        return jsonify({
            'status': 'success',
            'diagnostico': diagnostico
        })
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
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
        
        # Normalizar datos
        datos_normalizados = {}
        for field, value in datos.items():
            if field in VALID_VALUES:
                normalized = next(
                    (v for v in VALID_VALUES[field] if str(value).lower() == v.lower()),
                    None
                )
                if normalized is None:
                    normalized = VALID_VALUES[field][0]
                    logger.warning(f"Valor inválido para {field}: {value}. Usando: {normalized}")
                datos_normalizados[field] = normalized
            else:
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
        }), 503
        
    except Exception as e:
        logger.error(f"Error inesperado en predicción: {str(e)}")
        return jsonify({
            'error': "Error interno del servidor",
            'status': 'error',
            'tipo_error': 'interno'
        }), 500


# ---------- Funciones auxiliares del modelo ----------

def predecir_reservas(data):
    """
    Función simulada para predecir reservas.
    Reemplaza este contenido por tu lógica real usando ML o heurísticas.
    """
    # Simulación: sumamos personas + anticipacion
    personas = data.get("personas", 1)
    anticipacion = data.get("anticipacion", 1)
    resultado_simulado = int((personas + anticipacion) / 2)
    return resultado_simulado


def verificar_estado_modelo():
    """
    Verifica si el modelo está disponible (simulado)
    """
    return "modelo cargado correctamente"


def diagnosticar_modelo():
    """
    Devuelve métricas simuladas del modelo
    """
    return {
        "precision": 0.89,
        "recall": 0.91,
        "f1_score": 0.90
    }
    
def verificar_y_cargar_modelo():
    """
    Simula la carga de un modelo. Puedes reemplazar esto con la carga real desde un archivo .pkl u otro.
    """
    try:
        # Aquí iría la lógica real como por ejemplo:
        # with open("modelo_entrenado.pkl", "rb") as f:
        #     modelo = pickle.load(f)
        modelo = "modelo_simulado"  # Simulación
        return modelo
    except Exception as e:
        logger.error(f"❌ Error al cargar el modelo: {str(e)}")
        raise RuntimeError("No se pudo cargar el modelo") from e