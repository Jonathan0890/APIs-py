from flask import Blueprint, request, jsonify

insights_bp = Blueprint('insights_bp', __name__)

@insights_bp.route('/', methods=['POST'])
def generate_insights():
    try:
        # Para debug: imprime lo que recibes
        print("Datos recibidos:", request.json)
        
        data = request.get_json()
        predicciones = data.get('predicciones', [])
        
        if not predicciones:
            return jsonify({"error": "No se proporcionaron predicciones"}), 400
        
        # Respuesta de prueba simple
        reporte = f"Análisis de {len(predicciones)} predicciones:\n"
        reporte += f"- Valor recibido: {predicciones[0]}\n"
        reporte += "- Este es un reporte de prueba"
        
        return jsonify({"reporte": reporte})
        
    except Exception as e:
        print("Error en insights:", str(e))
        return jsonify({"error": str(e)}), 500