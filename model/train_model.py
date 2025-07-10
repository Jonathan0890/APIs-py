import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import logging

logger = logging.getLogger(__name__)

CATEGORIAS = {
    'estado': ['confirmed', 'cancelled_by_guest'],
    'tipo de unidad': ['twin_room', 'doble', 'suite', 'individual'],
    'motivo del viaje': ['ocio', 'trabajo'],
    'dispositivos': ['movil', 'ordenador'],
    'dia_semana': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
}

def normalizar_categoria(valor, categoria):
    valor = str(valor).strip().lower()
    for val in CATEGORIAS[categoria]:
        if valor == val.lower():
            return val
    return CATEGORIAS[categoria][0]

def entrenar_modelo_si_no_existe():
    try:
        os.makedirs('modelo', exist_ok=True)
        ruta_datos = os.path.join('reservas', 'datos_limpios.xlsx')
        
        if not os.path.exists(ruta_datos):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_datos}")

        logger.info("Cargando datos...")
        df = pd.read_excel(ruta_datos)

        # Renombrar columnas
        columnas_renombrar = {
            'Entrada': 'entrada',
            'Salida': 'salida',
            'Fecha de reserva': 'fecha de reserva',
            'Tipo de unidad': 'tipo de unidad',
            'Adultos': 'adulto',
            'Niños': 'niños',
            'Personas': 'personas',
            'Estado': 'estado',
            'Dispositivo': 'dispositivos',
            'Motivo del viaje': 'motivo del viaje',
            'Número de reserva': 'numero de reserva'
        }
        df.rename(columns=columnas_renombrar, inplace=True)

        # Normalizar categorías
        logger.info("Normalizando datos...")
        for cat in CATEGORIAS:
            if cat in df.columns:
                df[cat] = df[cat].apply(lambda x: normalizar_categoria(x, cat))

        # Procesar fechas
        df['entrada'] = pd.to_datetime(df['entrada'], errors='coerce')
        df['salida'] = pd.to_datetime(df['salida'], errors='coerce')
        df['fecha de reserva'] = pd.to_datetime(df['fecha de reserva'], errors='coerce')
        df = df.dropna(subset=['entrada'])

        # Calcular características
        df['duracion(noches)'] = (df['salida'] - df['entrada']).dt.days
        df['dia_semana'] = df['entrada'].dt.strftime('%A').str.lower()
        df['mes'] = df['entrada'].dt.month
        df['anio'] = df['entrada'].dt.year
        df['anticipacion'] = (df['entrada'] - df['fecha de reserva']).dt.days

        # Agrupar datos
        logger.info("Agrupando datos...")
        df_agregado = df.groupby(['entrada', 'dia_semana', 'mes', 'anio']).agg({
            'duracion(noches)': 'mean',
            'tipo de unidad': lambda x: x.mode()[0] if not x.mode().empty else CATEGORIAS['tipo de unidad'][0],
            'personas': 'mean',
            'adulto': 'mean',
            'niños': 'mean',
            'motivo del viaje': lambda x: x.mode()[0] if not x.mode().empty else CATEGORIAS['motivo del viaje'][0],
            'dispositivos': lambda x: x.mode()[0] if not x.mode().empty else CATEGORIAS['dispositivos'][0],
            'anticipacion': 'mean',
            'estado': lambda x: x.mode()[0] if not x.mode().empty else CATEGORIAS['estado'][0],
            'numero de reserva': 'count'
        }).reset_index().rename(columns={'numero de reserva': 'reservas'})

        # Codificar categorías
        logger.info("Codificando variables...")
        le_dict = {}
        for col in CATEGORIAS:
            le = LabelEncoder()
            df_agregado[col] = le.fit_transform(df_agregado[col])
            le_dict[col] = le

        # Entrenar modelo
        logger.info("Entrenando modelo...")
        X = df_agregado[list(CATEGORIAS.keys()) + ['mes', 'anio', 'duracion(noches)', 'personas', 'adulto', 'niños', 'anticipacion']]
        y = df_agregado['reservas']

        modelo = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        modelo.fit(X, y)

        # Guardar modelo
        logger.info("Guardando modelo...")
        joblib.dump(modelo, 'modelo/modelo.pkl')
        joblib.dump(le_dict, 'modelo/codificadores.pkl')

        logger.info("✅ Modelo entrenado exitosamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error en entrenamiento: {str(e)}")
        raise