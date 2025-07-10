import os
import logging
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from routes.predic_route import predict_bp

# Configuración inicial
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cargar modelo al iniciar
try:
    from model.predictor import verificar_y_cargar_modelo
    logger.info("Cargando modelo ML...")
    verificar_y_cargar_modelo()
    logger.info("✅ Modelo ML cargado correctamente")
except Exception as e:
    logger.error(f"❌ Error al cargar el modelo: {str(e)}")
    raise RuntimeError("No se pudo cargar el modelo") from e

# Registrar blueprints
app.register_blueprint(predict_bp, url_prefix='/api/prediccion')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)