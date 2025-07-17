import os
import logging
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from routes.predic_route import predict_bp
from routes.insights_route import insights_bp
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import LabelEncoder
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import io
from datetime import datetime

# Configuración inicial
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cargar modelo al iniciar y datos
try:
    from model.predictor import verificar_y_cargar_modelo
    logger.info("Cargando modelo ML...")
    verificar_y_cargar_modelo()
    logger.info("✅ Modelo ML cargado correctamente")
    
    # Cargar datos del hotel
    logger.info("Cargando datos del hotel...")
    df = pd.read_excel("datos_limpios.xlsx")
    
    # Preprocesamiento básico
    df['Entrada'] = pd.to_datetime(df['Entrada'])
    df['Fecha de reserva'] = pd.to_datetime(df['Fecha de reserva'])
    df['Dia_semana'] = df['Entrada'].dt.dayofweek
    df['Mes'] = df['Entrada'].dt.month
    df['Año'] = df['Entrada'].dt.year
    
    # Codificadores para cancelaciones
    le_motivo = LabelEncoder()
    le_pais = LabelEncoder()
    df['Motivo_num'] = le_motivo.fit_transform(df['Motivo del viaje'])
    df['Pais_num'] = le_pais.fit_transform(df['Booker country'])
    
    logger.info("✅ Datos del hotel cargados correctamente")
    
except Exception as e:
    logger.error(f"❌ Error al cargar datos o modelos: {str(e)}")
    raise RuntimeError("No se pudo cargar los datos o modelos") from e

# Registrar blueprints
app.register_blueprint(predict_bp, url_prefix='/api/prediccion')
app.register_blueprint(insights_bp, url_prefix='/api/insights')

# Rutas de los templates
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 1. Predicción de Reservas
@app.route('/prediccion_reservas', methods=['GET', 'POST'])
def prediccion_reservas():
    try:
        # Verificar si hay datos suficientes
        if len(df) == 0:
            raise ValueError("No hay datos disponibles para realizar predicciones")
            
        # Preparar datos históricos
        reservas_por_dia = df.groupby(['Año', 'Mes', 'Dia_semana']).size().reset_index(name='Num_reservas')
        
        # Verificar que hay datos históricos
        if len(reservas_por_dia) == 0:
            raise ValueError("No hay suficientes datos históricos para entrenar el modelo")
            
        X = reservas_por_dia[['Año', 'Mes', 'Dia_semana']]
        y = reservas_por_dia['Num_reservas']
        
        # Entrenar modelo
        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X, y)
        
        # Variables para el template
        resultado = None
        datos_usuario = {}
        grafica_img = None
        historico_img = None
        nombre_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        nombre_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        if request.method == 'POST':
            fecha_str = request.form['fecha']
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            
            # Datos para la predicción
            datos_usuario = {
                'Año': fecha.year,
                'Mes': fecha.month,
                'Dia_semana': fecha.weekday()
            }
            
            # Realizar predicción
            entrada = pd.DataFrame([datos_usuario])
            pred = int(modelo.predict(entrada)[0])
            
            # Formatear resultado
            dia_nombre = nombre_dias[fecha.weekday()]
            mes_nombre = nombre_meses[fecha.month - 1]
            resultado = f"Se predice que el {dia_nombre} {fecha.day} de {mes_nombre} del {fecha.year} habrá {pred} reservas."
            
            # Gráfico 1: Importancia de características
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            importancias = modelo.feature_importances_
            features = ['Año', 'Mes', 'Día semana']
            ax1.barh(features, importancias, color=['#3b82f6', '#10b981', '#6366f1'])
            ax1.set_title('Factores que influyen en la predicción')
            ax1.set_xlabel('Importancia relativa')
            buf1 = io.BytesIO()
            plt.savefig(buf1, format='png', bbox_inches='tight')
            buf1.seek(0)
            grafica_img = base64.b64encode(buf1.read()).decode('utf-8')
            plt.close(fig1)
            
            # Gráfico 2: Datos históricos para contexto
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            
            # Filtrar datos históricos del mismo mes
            historico = df[df['Mes'] == fecha.month].groupby('Dia_semana').size()
            
            if len(historico) > 0:
                historico.index = [nombre_dias[i] for i in historico.index]
                historico.plot(kind='bar', ax=ax2, color='#3b82f6', alpha=0.7)
                ax2.axhline(pred, color='#ef4444', linestyle='--', label='Predicción actual')
                ax2.set_title(f'Reservas históricas para {mes_nombre}')
                ax2.set_ylabel('Número de reservas')
                ax2.legend()
            else:
                # Mostrar mensaje si no hay datos históricos
                ax2.text(0.5, 0.5, 'No hay datos históricos\npara este mes', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title(f'Reservas históricas para {mes_nombre}')
            
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', bbox_inches='tight')
            buf2.seek(0)
            historico_img = base64.b64encode(buf2.read()).decode('utf-8')
            plt.close(fig2)
            
    except Exception as e:
        logger.error(f"Error en predicción de reservas: {str(e)}")
        resultado = f"Error: {str(e)}"
        grafica_img = None
        historico_img = None
    
    return render_template("prediccion_reservas.html",
                         resultado=resultado,
                         datos_usuario=datos_usuario,
                         grafica_img=grafica_img,
                         historico_img=historico_img)

# 2. Predicción de Tipo de Habitación
@app.route('/prediccion_habitacion', methods=['GET', 'POST'])
def prediccion_habitacion():
    df_habitaciones = df[df['Tipo de unidad'].notna()]
    X = df_habitaciones[['Personas', 'Adultos', 'Niños']]
    y = df_habitaciones['Tipo de unidad']
    
    modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
    modelo.fit(X, y)
    
    resultado = None
    datos_usuario = {}
    arbol_img = None
    
    if request.method == 'POST':
        try:
            datos_usuario = {
                'Personas': int(request.form['personas']),
                'Adultos': int(request.form['adultos']),
                'Niños': int(request.form['ninos'])
            }
            
            entrada = pd.DataFrame([datos_usuario])
            pred = modelo.predict(entrada)[0]
            resultado = f"Tipo de habitación recomendada: {pred}"
            
            # Visualizar árbol
            fig, ax = plt.subplots(figsize=(12, 8))
            plot_tree(modelo, feature_names=['Personas', 'Adultos', 'Niños'], 
                     class_names=modelo.classes_, filled=True, rounded=True)
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            arbol_img = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error en predicción de habitación: {str(e)}")
            resultado = f"Error: {str(e)}"
    
    return render_template("prediccion_habitacion.html",
                         resultado=resultado,
                         datos_usuario=datos_usuario,
                         arbol_img=arbol_img)

# 3. Predicción de Duración de Estancia
@app.route('/prediccion_estancia', methods=['GET', 'POST'])
def prediccion_estancia():
    df_estancia = df[df['Duración (noches)'].notna()]
    le_motivo = LabelEncoder()
    df_estancia['Motivo_num'] = le_motivo.fit_transform(df_estancia['Motivo del viaje'])
    
    X = df_estancia[['Personas', 'Dia_semana', 'Mes', 'Motivo_num']]
    y = df_estancia['Duración (noches)']
    
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    resultado = None
    datos_usuario = {}
    coef_img = None
    
    if request.method == 'POST':
        try:
            datos_usuario = {
                'Personas': int(request.form['personas']),
                'Dia_semana': int(request.form['dia_semana']),
                'Mes': int(request.form['mes']),
                'Motivo': request.form['motivo']
            }
            
            motivo_num = le_motivo.transform([datos_usuario['Motivo']])[0]
            
            entrada = pd.DataFrame([[datos_usuario['Personas'], 
                                  datos_usuario['Dia_semana'], 
                                  datos_usuario['Mes'], 
                                  motivo_num]]).T
            entrada.columns = ['Personas', 'Dia_semana', 'Mes', 'Motivo_num']
            
            pred = round(modelo.predict(entrada)[0], 1)
            resultado = f"Duración estimada de la estancia: {pred} noches"
            
            # Gráfico de coeficientes
            fig, ax = plt.subplots()
            coef = pd.Series(modelo.coef_, index=['Personas', 'Día semana', 'Mes', 'Motivo'])
            coef.plot(kind='barh')
            ax.set_title('Impacto de cada variable')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            coef_img = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error en predicción de estancia: {str(e)}")
            resultado = f"Error: {str(e)}"
    
    return render_template("prediccion_estancia.html",
                         resultado=resultado,
                         datos_usuario=datos_usuario,
                         coef_img=coef_img,
                         motivos=le_motivo.classes_)

# 4. Predicción de Cancelación
@app.route('/prediccion_cancelacion', methods=['GET', 'POST'])
def prediccion_cancelacion():
    df['Cancelado'] = (df['Estado'] == 'Cancelada').astype(int)
    df['Dias_anticipacion'] = (df['Entrada'] - df['Fecha de reserva']).dt.days
    
    X = df[['Personas', 'Dias_anticipacion', 'Motivo_num', 'Pais_num', 'Dia_semana']]
    y = df['Cancelado']
    
    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(X, y)
    
    resultado = None
    datos_usuario = {}
    proba_img = None
    
    if request.method == 'POST':
        try:
            datos_usuario = {
                'Personas': int(request.form['personas']),
                'Dias_anticipacion': int(request.form['dias_anticipacion']),
                'Motivo': request.form['motivo'],
                'Pais': request.form['pais'],
                'Dia_semana': int(request.form['dia_semana'])
            }
            
            motivo_num = le_motivo.transform([datos_usuario['Motivo']])[0]
            pais_num = le_pais.transform([datos_usuario['Pais']])[0]
            
            entrada = pd.DataFrame([[datos_usuario['Personas'], 
                                   datos_usuario['Dias_anticipacion'], 
                                   motivo_num, 
                                   pais_num, 
                                   datos_usuario['Dia_semana']]]).T
            entrada.columns = ['Personas', 'Dias_anticipacion', 'Motivo_num', 'Pais_num', 'Dia_semana']
            
            proba = modelo.predict_proba(entrada)[0][1]
            pred = "Sí" if proba >= 0.5 else "No"
            resultado = f"Probabilidad de cancelación: {round(proba*100, 1)}% - Predicción: {pred}"
            
            # Gráfico de probabilidades
            fig, ax = plt.subplots()
            ax.bar(['No cancelar', 'Cancelar'], [1-proba, proba], color=['green', 'red'])
            ax.set_ylim(0, 1)
            ax.set_title('Probabilidad de cancelación')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            proba_img = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error en predicción de cancelación: {str(e)}")
            resultado = f"Error: {str(e)}"
    
    return render_template("prediccion_cancelacion.html",
                         resultado=resultado,
                         datos_usuario=datos_usuario,
                         proba_img=proba_img,
                         motivos=le_motivo.classes_,
                         paises=le_pais.classes_)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "data_loaded": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)