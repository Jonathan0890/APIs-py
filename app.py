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
    
    
    logger.info("Cargando datos del hotel...")
    df = pd.read_excel("datos_limpios2.xlsx")
    
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
    try:
        # Filtrar datos válidos
        df_habitaciones = df[df['Tipo de unidad'].notna()]
        
        # Verificar que hay datos
        if len(df_habitaciones) == 0:
            raise ValueError("No hay datos de habitaciones disponibles")
            
        # Usar solo adultos y niños como features
        X = df_habitaciones[['Adultos', 'Niños']]
        y = df_habitaciones['Tipo de unidad']
        
        # Entrenar modelo
        modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
        modelo.fit(X, y)
        
        resultado = None
        datos_usuario = {}
        arbol_img = None
        
        if request.method == 'POST':
            try:
                # Obtener datos del formulario (solo adultos y niños)
                adultos = int(request.form['adultos'])
                ninos = int(request.form['ninos'])
                
                # Calcular total de personas
                total_personas = adultos + ninos
                
                datos_usuario = {
                    'Adultos': adultos,
                    'Niños': ninos,
                    'Personas': total_personas
                }
                
                # Realizar predicción
                entrada = pd.DataFrame([[adultos, ninos]], columns=['Adultos', 'Niños'])
                pred = modelo.predict(entrada)[0]
                resultado = f"Tipo de habitación recomendada: {pred}"
                
                # Visualizar árbol
                from sklearn.tree import plot_tree  # Importar aquí para evitar error
                
                fig, ax = plt.subplots(figsize=(16, 10))
                plot_tree(modelo, 
                         feature_names=['Adultos', 'Niños'],
                         class_names=modelo.classes_,
                         filled=True, 
                         rounded=True,
                         proportion=True,
                         fontsize=10,
                         ax=ax)
                
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
                buf.seek(0)
                arbol_img = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
                
            except Exception as e:
                logger.error(f"Error en predicción de habitación: {str(e)}")
                resultado = f"Error: {str(e)}"
        
        return render_template("prediccion_habitacion.html",
                             resultado=resultado,
                             datos_usuario=datos_usuario,
                             arbol_img=arbol_img)
    
    except Exception as e:
        logger.error(f"Error inicial en predicción de habitación: {str(e)}")
        return render_template("prediccion_habitacion.html",
                             resultado=f"Error: {str(e)}",
                             datos_usuario={},
                             arbol_img=None)

# 3. Predicción de Duración de Estanci
@app.route('/prediccion_estancia', methods=['GET', 'POST'])
def prediccion_estancia():
    try:
        # Hacer una copia del dataframe para no modificar el original
        df_estancia = df.copy()
        df_estancia = df_estancia[df_estancia['Motivo del viaje'].isin(['Trabajo', 'Ocio'])]
        
        # Codificadores
        le_motivo = LabelEncoder()
        le_pais = LabelEncoder()
        
        df_estancia['Motivo_num'] = le_motivo.fit_transform(df_estancia['Motivo del viaje'])
        df_estancia['Pais_num'] = le_pais.fit_transform(df_estancia['Booker country'])
        
        # Preparar datos para el modelo
        X = df_estancia[['Personas', 'Dia_semana', 'Mes', 'Motivo_num', 'Pais_num']]
        y = df_estancia['Duración (noches)']
        
        # Entrenar modelo
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        
        todos_los_paises = [
            "afganistán(af)", "albania(al)", "alemania(de)", "andorra(ad)", "angola(ao)",
            "anguilla(ai)", "antártida(aq)", "antigua y barbuda(ag)", "antillas holandesas(an)",
            "arabia saudí(sa)", "argelia(dz)", "argentina(ar)", "armenia(am)", "aruba(aw)",
            "australia(au)", "austria(at)", "azerbaiyán(az)", "bahamas(bs)", "bahrein(bh)",
            "bangladesh(bd)", "barbados(bb)", "bélgica(be)", "belice(bz)", "benin(bj)",
            "bermudas(bm)", "bielorrusia(by)", "birmania(mm)", "bolivia(bo)", "bosnia y herzegovina(ba)",
            "botswana(bw)", "brasil(br)", "brunei(bn)", "bulgaria(bg)", "burkina faso(bf)",
            "burundi(bi)", "bután(bt)", "cabo verde(cv)", "camboya(kh)", "camerún(cm)",
            "canadá(ca)", "chad(td)", "chile(cl)", "china(cn)", "chipre(cy)",
            "ciudad del vaticano (santa sede)(va)", "colombia(co)", "comores(km)", "congo(cg)",
            "congo, república democrática del(cd)", "corea(kr)", "corea del norte(kp)", "costa de marfíl(ci)",
            "costa rica(cr)", "croacia (hrvatska)(hr)", "cuba(cu)", "dinamarca(dk)", "djibouti(dj)",
            "dominica(dm)", "ecuador(ec)", "egipto(eg)", "el salvador(sv)", "emiratos árabes unidos(ae)",
            "eritrea(er)", "eslovenia(si)", "españa(es)", "estados unidos(us)", "estonia(ee)",
            "etiopía(et)", "fiji(fj)", "filipinas(ph)", "finlandia(fi)", "francia(fr)",
            "gabón(ga)", "gambia(gm)", "georgia(ge)", "ghana(gh)", "gibraltar(gi)",
            "granada(gd)", "grecia(gr)", "groenlandia(gl)", "guadalupe(gp)", "guam(gu)",
            "guatemala(gt)", "guayana(gy)", "guayana francesa(gf)", "guinea(gn)", "guinea ecuatorial(gq)",
            "guinea-bissau(gw)", "haití(ht)", "honduras(hn)", "hungría(hu)", "india(in)",
            "indonesia(id)", "irak(iq)", "irán(ir)", "irlanda(ie)", "isla bouvet(bv)",
            "isla de christmas(cx)", "islandia(is)", "islas caimán(ky)", "islas cook(ck)",
            "islas de cocos o keeling(cc)", "islas faroe(fo)", "islas heard y mcdonald(hm)", "islas malvinas(fk)",
            "islas marianas del norte(mp)", "islas marshall(mh)", "islas menores de estados unidos(um)", "islas palau(pw)",
            "islas salomón(sb)", "islas svalbard y jan mayen(sj)", "islas tokelau(tk)", "islas turks y caicos(tc)",
            "islas vírgenes (eeuu)(vi)", "islas vírgenes (reino unido)(vg)", "islas wallis y futuna(wf)", "israel(il)",
            "italia(it)", "jamaica(jm)", "japón(jp)", "jordania(jo)", "kazajistán(kz)",
            "kenia(ke)", "kirguizistán(kg)", "kiribati(ki)", "kuwait(kw)", "laos(la)",
            "lesotho(ls)", "letonia(lv)", "líbano(lb)", "liberia(lr)", "libia(ly)",
            "liechtenstein(li)", "lituania(lt)", "luxemburgo(lu)", "macedonia, ex-república yugoslava de(mk)", "madagascar(mg)",
            "malasia(my)", "malawi(mw)", "maldivas(mv)", "malí(ml)", "malta(mt)",
            "marruecos(ma)", "martinica(mq)", "mauricio(mu)", "mauritania(mr)", "mayotte(yt)",
            "méxico(mx)", "micronesia(fm)", "moldavia(md)", "mónaco(mc)", "mongolia(mn)",
            "montserrat(ms)", "mozambique(mz)", "namibia(na)", "nauru(nr)", "nepal(np)",
            "nicaragua(ni)", "níger(ne)", "nigeria(ng)", "niue(nu)", "norfolk(nf)",
            "noruega(no)", "nueva caledonia(nc)", "nueva zelanda(nz)", "omán(om)", "países bajos(nl)",
            "panamá(pa)", "papúa nueva guinea(pg)", "paquistán(pk)", "paraguay(py)", "perú(pe)",
            "pitcairn(pn)", "polinesia francesa(pf)", "polonia(pl)", "portugal(pt)", "puerto rico(pr)",
            "qatar(qa)", "reino unido(uk)", "república centroafricana(cf)", "república checa(cz)", "república de sudáfrica(za)",
            "república dominicana(do)", "república eslovaca(sk)", "reunión(re)", "ruanda(rw)", "rumania(ro)",
            "rusia(ru)", "sahara occidental(eh)", "saint kitts y nevis(kn)", "samoa(ws)", "samoa americana(as)",
            "san marino(sm)", "san vicente y granadinas(vc)", "santa elena(sh)", "santa lucía(lc)", "santo tomé y príncipe(st)",
            "senegal(sn)", "seychelles(sc)", "sierra leona(sl)", "singapur(sg)", "siria(sy)",
            "somalia(so)", "sri lanka(lk)", "st pierre y miquelon(pm)", "suazilandia(sz)", "sudán(sd)",
            "suecia(se)", "suiza(ch)", "surinam(sr)", "tailandia(th)", "taiwán(tw)",
            "tanzania(tz)", "tayikistán(tj)", "territorios franceses del sur(tf)", "timor oriental(tp)", "togo(tg)",
            "tonga(to)", "trinidad y tobago(tt)", "túnez(tn)", "turkmenistán(tm)", "turquía(tr)",
            "tuvalu(tv)", "ucrania(ua)", "uganda(ug)", "uruguay(uy)", "uzbekistán(uz)",
            "vanuatu(vu)", "venezuela(ve)", "vietnam(vn)", "yemen(ye)", "yugoslavia(yu)",
            "zambia(zm)", "zimbabue(zw)"
        ]
        
        # Preparar variables para el template
        resultado = None
        datos_usuario = {}
        coef_img = None
        regresion_img = None
        analisis_pais = None
        nombre_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        nombre_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        if request.method == 'POST':
            try:
                # Obtener datos del formulario
                datos_usuario = {
                    'Personas': int(request.form['personas']),
                    'Dia_semana': int(request.form['dia_semana']),
                    'Mes': int(request.form['mes']),
                    'Motivo': request.form['motivo'],
                    'Pais': request.form.get('pais', 'es').lower()  # Default a España si no se especifica
                }
                
                # Verificar si el país está en los datos
                pais_en_datos = datos_usuario['Pais'] in le_pais.classes_
                
                # Preparar datos para predicción
                motivo_num = le_motivo.transform([datos_usuario['Motivo']])[0]
                pais_num = le_pais.transform([datos_usuario['Pais']])[0] if pais_en_datos else le_pais.transform(['es'])[0]
                
                entrada = pd.DataFrame([[datos_usuario['Personas'], 
                                      datos_usuario['Dia_semana'], 
                                      datos_usuario['Mes'], 
                                      motivo_num, 
                                      pais_num]])
                
                # Realizar predicción
                pred = round(modelo.predict(entrada)[0], 1)
                resultado = f"Duración estimada: {pred} noches"
                
                # Generar análisis por país y motivo
                if pais_en_datos:
                    filtro_pais = (df_estancia['Booker country'] == datos_usuario['Pais']) & \
                                 (df_estancia['Motivo del viaje'] == datos_usuario['Motivo']) & \
                                 (df_estancia['Mes'] == datos_usuario['Mes'])
                    
                    if filtro_pais.any():
                        duracion_promedio = df_estancia[filtro_pais]['Duración (noches)'].mean()
                        tendencia = "largas" if duracion_promedio > 4 else "cortas"
                        
                        nombre_pais = next((p.split('(')[0] for p in todos_los_paises 
                                          if p.split('(')[1].replace(')', '') == datos_usuario['Pais']), datos_usuario['Pais'].upper())
                        
                        analisis_pais = {
                            'mensaje': f"Las personas de {nombre_pais} que vienen por motivos de {datos_usuario['Motivo'].lower()} en {nombre_meses[datos_usuario['Mes']-1]} son más propensas a estancias {tendencia} (promedio: {duracion_promedio:.1f} noches).",
                            'tendencia': tendencia,
                            'duracion_promedio': duracion_promedio
                        }
                
                # Gráfico de coeficientes
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                features = ['Personas', 'Día semana', 'Mes', 'Motivo', 'País']
                importancias = np.abs(modelo.coef_)  # Usamos valor absoluto para importancia
                ax1.barh(features, importancias, color=['#3b82f6', '#10b981', '#6366f1', '#f59e0b', '#ec4899'])
                ax1.set_title('Impacto de cada variable en la duración')
                ax1.set_xlabel('Importancia relativa')
                buf1 = io.BytesIO()
                plt.savefig(buf1, format='png', bbox_inches='tight')
                buf1.seek(0)
                coef_img = base64.b64encode(buf1.read()).decode('utf-8')
                plt.close(fig1)
                
                # Gráfico de regresión lineal (relación entre personas y duración)
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                
                # Agrupar por número de personas
                datos_agrupados = df_estancia.groupby('Personas')['Duración (noches)'].mean()
                
                # Gráfico de dispersión con línea de regresión (usando matplotlib directamente)
                ax2.scatter(df_estancia['Personas'], df_estancia['Duración (noches)'], 
                           alpha=0.3, color='#3b82f6', label='Datos históricos')
                
                # Añadir línea de regresión
                x_vals = np.array(ax2.get_xlim())
                y_vals = modelo.intercept_ + modelo.coef_[0] * x_vals
                ax2.plot(x_vals, y_vals, color='#ef4444', label='Tendencia general')
                
                # Destacar la predicción actual
                ax2.scatter(datos_usuario['Personas'], pred, color='#10b981', s=100, label='Predicción actual')
                
                ax2.set_xlabel('Número de Personas')
                ax2.set_ylabel('Duración (noches)')
                ax2.set_title('Relación entre número de personas y duración de estancia')
                ax2.legend()
                plt.tight_layout()
                
                buf2 = io.BytesIO()
                plt.savefig(buf2, format='png', dpi=100)
                buf2.seek(0)
                regresion_img = base64.b64encode(buf2.read()).decode('utf-8')
                plt.close(fig2)
                
            except Exception as e:
                logger.error(f"Error en predicción de estancia: {str(e)}")
                resultado = f"Error: {str(e)}"
        
        return render_template("prediccion_estancia.html",
                            resultado=resultado,
                            datos_usuario=datos_usuario,
                            coef_img=coef_img,
                            regresion_img=regresion_img,
                            analisis_pais=analisis_pais,
                            motivos=['Trabajo', 'Ocio'],
                            todos_los_paises=todos_los_paises,
                            nombre_meses=nombre_meses,
                            nombre_dias=nombre_dias)
    
    except Exception as e:
        logger.error(f"Error inicial en predicción de estancia: {str(e)}")
        return render_template("prediccion_estancia.html",
                            resultado=f"Error: {str(e)}",
                            datos_usuario={},
                            coef_img=None,
                            regresion_img=None,
                            analisis_pais=None,
                            motivos=['Trabajo', 'Ocio'],
                            todos_los_paises=[],
                            nombre_meses=[],
                            nombre_dias=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])

# 4. Predicción de Cancelación
@app.route('/prediccion_cancelacion', methods=['GET', 'POST'])
def prediccion_cancelacion():
    try:
        # Hacer una copia del dataframe para no modificar el original
        df_cancel = df.copy()
        
        # Preparar datos
        df_cancel['Cancelado'] = (df_cancel['Estado'] == 'Cancelada').astype(int)
        df_cancel['Dias_anticipacion'] = (df_cancel['Entrada'] - df_cancel['Fecha de reserva']).dt.days
        
        # Filtrar solo motivos válidos (trabajo o ocio)
        df_cancel = df_cancel[df_cancel['Motivo del viaje'].isin(['Trabajo', 'Ocio'])]
        
        # Verificar que hay datos de ambas clases
        if df_cancel['Cancelado'].nunique() < 2:
            # Crear datos de ejemplo si no hay suficientes
            logger.warning("Creando datos de ejemplo para demostración...")
            ejemplo_data = {
                'Personas': [2, 1, 4, 2, 3],
                'Dias_anticipacion': [7, 30, 3, 14, 21],
                'Motivo del viaje': ['Trabajo', 'Ocio', 'Ocio', 'Trabajo', 'Ocio'],
                'Booker country': ['mx', 'us', 'br', 'es', 'co'],  # En minúsculas
                'Dia_semana': [0, 4, 6, 2, 3],
                'Estado': ['Confirmada', 'Cancelada', 'Confirmada', 'Cancelada', 'Confirmada']
            }
            df_ejemplo = pd.DataFrame(ejemplo_data)
            df_ejemplo['Cancelado'] = (df_ejemplo['Estado'] == 'Cancelada').astype(int)
            df_ejemplo['Entrada'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(np.random.randint(0, 30, len(df_ejemplo)), unit='d')
            df_ejemplo['Fecha de reserva'] = df_ejemplo['Entrada'] - pd.to_timedelta(df_ejemplo['Dias_anticipacion'], unit='d')
            
            df_cancel = pd.concat([df_cancel, df_ejemplo])
        
        # Codificadores
        le_motivo = LabelEncoder()
        le_pais = LabelEncoder()
        
        df_cancel['Motivo_num'] = le_motivo.fit_transform(df_cancel['Motivo del viaje'])
        df_cancel['Pais_num'] = le_pais.fit_transform(df_cancel['Booker country'])
        
        # Tasa de cancelación por país
        cancelacion_por_pais = df_cancel.groupby('Booker country')['Cancelado'].mean()
        
        # Lista de países con datos históricos (en minúsculas)
        paises_con_datos = sorted(df_cancel['Booker country'].unique())
        
        X = df_cancel[['Personas', 'Dias_anticipacion', 'Motivo_num', 'Pais_num', 'Dia_semana']]
        y = df_cancel['Cancelado']
        
        # Entrenar modelo
        modelo = LogisticRegression(max_iter=1000, class_weight='balanced')
        modelo.fit(X, y)
        
        resultado = None
        datos_usuario = {}
        proba_img = None
        regresion_img = None
        
        
        todos_los_paises = [
            "afganistán(af)", "albania(al)", "alemania(de)", "andorra(ad)", "angola(ao)",
            "anguilla(ai)", "antártida(aq)", "antigua y barbuda(ag)", "antillas holandesas(an)",
            "arabia saudí(sa)", "argelia(dz)", "argentina(ar)", "armenia(am)", "aruba(aw)",
            "australia(au)", "austria(at)", "azerbaiyán(az)", "bahamas(bs)", "bahrein(bh)",
            "bangladesh(bd)", "barbados(bb)", "bélgica(be)", "belice(bz)", "benin(bj)",
            "bermudas(bm)", "bielorrusia(by)", "birmania(mm)", "bolivia(bo)", "bosnia y herzegovina(ba)",
            "botswana(bw)", "brasil(br)", "brunei(bn)", "bulgaria(bg)", "burkina faso(bf)",
            "burundi(bi)", "bután(bt)", "cabo verde(cv)", "camboya(kh)", "camerún(cm)",
            "canadá(ca)", "chad(td)", "chile(cl)", "china(cn)", "chipre(cy)",
            "ciudad del vaticano (santa sede)(va)", "colombia(co)", "comores(km)", "congo(cg)",
            "congo, república democrática del(cd)", "corea(kr)", "corea del norte(kp)", "costa de marfíl(ci)",
            "costa rica(cr)", "croacia (hrvatska)(hr)", "cuba(cu)", "dinamarca(dk)", "djibouti(dj)",
            "dominica(dm)", "ecuador(ec)", "egipto(eg)", "el salvador(sv)", "emiratos árabes unidos(ae)",
            "eritrea(er)", "eslovenia(si)", "españa(es)", "estados unidos(us)", "estonia(ee)",
            "etiopía(et)", "fiji(fj)", "filipinas(ph)", "finlandia(fi)", "francia(fr)",
            "gabón(ga)", "gambia(gm)", "georgia(ge)", "ghana(gh)", "gibraltar(gi)",
            "granada(gd)", "grecia(gr)", "groenlandia(gl)", "guadalupe(gp)", "guam(gu)",
            "guatemala(gt)", "guayana(gy)", "guayana francesa(gf)", "guinea(gn)", "guinea ecuatorial(gq)",
            "guinea-bissau(gw)", "haití(ht)", "honduras(hn)", "hungría(hu)", "india(in)",
            "indonesia(id)", "irak(iq)", "irán(ir)", "irlanda(ie)", "isla bouvet(bv)",
            "isla de christmas(cx)", "islandia(is)", "islas caimán(ky)", "islas cook(ck)",
            "islas de cocos o keeling(cc)", "islas faroe(fo)", "islas heard y mcdonald(hm)", "islas malvinas(fk)",
            "islas marianas del norte(mp)", "islas marshall(mh)", "islas menores de estados unidos(um)", "islas palau(pw)",
            "islas salomón(sb)", "islas svalbard y jan mayen(sj)", "islas tokelau(tk)", "islas turks y caicos(tc)",
            "islas vírgenes (eeuu)(vi)", "islas vírgenes (reino unido)(vg)", "islas wallis y futuna(wf)", "israel(il)",
            "italia(it)", "jamaica(jm)", "japón(jp)", "jordania(jo)", "kazajistán(kz)",
            "kenia(ke)", "kirguizistán(kg)", "kiribati(ki)", "kuwait(kw)", "laos(la)",
            "lesotho(ls)", "letonia(lv)", "líbano(lb)", "liberia(lr)", "libia(ly)",
            "liechtenstein(li)", "lituania(lt)", "luxemburgo(lu)", "macedonia, ex-república yugoslava de(mk)", "madagascar(mg)",
            "malasia(my)", "malawi(mw)", "maldivas(mv)", "malí(ml)", "malta(mt)",
            "marruecos(ma)", "martinica(mq)", "mauricio(mu)", "mauritania(mr)", "mayotte(yt)",
            "méxico(mx)", "micronesia(fm)", "moldavia(md)", "mónaco(mc)", "mongolia(mn)",
            "montserrat(ms)", "mozambique(mz)", "namibia(na)", "nauru(nr)", "nepal(np)",
            "nicaragua(ni)", "níger(ne)", "nigeria(ng)", "niue(nu)", "norfolk(nf)",
            "noruega(no)", "nueva caledonia(nc)", "nueva zelanda(nz)", "omán(om)", "países bajos(nl)",
            "panamá(pa)", "papúa nueva guinea(pg)", "paquistán(pk)", "paraguay(py)", "perú(pe)",
            "pitcairn(pn)", "polinesia francesa(pf)", "polonia(pl)", "portugal(pt)", "puerto rico(pr)",
            "qatar(qa)", "reino unido(uk)", "república centroafricana(cf)", "república checa(cz)", "república de sudáfrica(za)",
            "república dominicana(do)", "república eslovaca(sk)", "reunión(re)", "ruanda(rw)", "rumania(ro)",
            "rusia(ru)", "sahara occidental(eh)", "saint kitts y nevis(kn)", "samoa(ws)", "samoa americana(as)",
            "san marino(sm)", "san vicente y granadinas(vc)", "santa elena(sh)", "santa lucía(lc)", "santo tomé y príncipe(st)",
            "senegal(sn)", "seychelles(sc)", "sierra leona(sl)", "singapur(sg)", "siria(sy)",
            "somalia(so)", "sri lanka(lk)", "st pierre y miquelon(pm)", "suazilandia(sz)", "sudán(sd)",
            "suecia(se)", "suiza(ch)", "surinam(sr)", "tailandia(th)", "taiwán(tw)",
            "tanzania(tz)", "tayikistán(tj)", "territorios franceses del sur(tf)", "timor oriental(tp)", "togo(tg)",
            "tonga(to)", "trinidad y tobago(tt)", "túnez(tn)", "turkmenistán(tm)", "turquía(tr)",
            "tuvalu(tv)", "ucrania(ua)", "uganda(ug)", "uruguay(uy)", "uzbekistán(uz)",
            "vanuatu(vu)", "venezuela(ve)", "vietnam(vn)", "yemen(ye)", "yugoslavia(yu)",
            "zambia(zm)", "zimbabue(zw)"
        ]
        
        if request.method == 'POST':
            try:
                # Obtener datos del formulario
                datos_usuario = {
                    'Personas': int(request.form['personas']),
                    'Dias_anticipacion': int(request.form['dias_anticipacion']),
                    'Motivo': request.form['motivo'],
                    'Pais': request.form['pais'].lower(),  
                    'Dia_semana': int(request.form['dia_semana'])
                }
                
                # Verificar si hay datos para este país
                pais_con_datos = datos_usuario['Pais'] in paises_con_datos
                
                motivo_num = le_motivo.transform([datos_usuario['Motivo']])[0]
                pais_num = le_pais.transform([datos_usuario['Pais']])[0] if datos_usuario['Pais'] in le_pais.classes_ else -1
                
                entrada = pd.DataFrame([[datos_usuario['Personas'], 
                                      datos_usuario['Dias_anticipacion'], 
                                      motivo_num, 
                                      pais_num, 
                                      datos_usuario['Dia_semana']]])
                
                proba = modelo.predict_proba(entrada)[0][1]
                pred = "cancele" if proba >= 0.5 else "llegue"
                
                # Mensaje personalizado
                resultado = {
                    'prediccion': f"Basado en estos datos comparándolos con patrones de cancelación anteriores, es probable que el cliente que hizo esta reserva la {pred}.",
                    'probabilidad': round(proba * 100, 1),
                    'decision': pred,
                    'pais_actual': datos_usuario['Pais'],
                    'pais_con_datos': pais_con_datos,
                    'tasa_pais_actual': round(cancelacion_por_pais.get(datos_usuario['Pais'], 0) * 100) if pais_con_datos else 0
                }
                
                # Gráfico de probabilidades
                fig1, ax1 = plt.subplots(figsize=(8, 4))
                bars = ax1.bar(['No cancelar', 'Cancelar'], 
                            [1-proba, proba], 
                            color=['#10b981', '#ef4444'])
                
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1%}',
                            ha='center', va='bottom')
                
                ax1.set_ylim(0, 1)
                ax1.set_title('Probabilidad de Cancelación', pad=20)
                ax1.set_ylabel('Probabilidad')
                plt.tight_layout()
                
                buf1 = io.BytesIO()
                plt.savefig(buf1, format='png', dpi=100)
                buf1.seek(0)
                proba_img = base64.b64encode(buf1.read()).decode('utf-8')
                plt.close(fig1)
                
                # Gráfico de regresión logística (relación entre días de anticipación y cancelación)
                fig2, ax2 = plt.subplots(figsize=(8, 4))
                
                # Crear puntos para la curva de regresión
                x_test = np.linspace(df_cancel['Dias_anticipacion'].min(), 
                                   df_cancel['Dias_anticipacion'].max(), 
                                   300).reshape(-1, 1)
                
                # Mantener otras variables constantes (promedio) para el gráfico
                avg_personas = df_cancel['Personas'].mean()
                avg_motivo = df_cancel['Motivo_num'].mean()
                avg_pais = df_cancel['Pais_num'].mean()
                avg_dia = df_cancel['Dia_semana'].mean()
                
                # Crear matriz de características para predicción
                X_test = np.column_stack((
                    np.full_like(x_test, avg_personas),
                    x_test,
                    np.full_like(x_test, avg_motivo),
                    np.full_like(x_test, avg_pais),
                    np.full_like(x_test, avg_dia)
                ))
                
                # Predecir probabilidades
                y_proba = modelo.predict_proba(X_test)[:, 1]
                
                # Graficar
                ax2.plot(x_test, y_proba, color='#3b82f6', linewidth=2)
                ax2.scatter(df_cancel['Dias_anticipacion'], 
                           df_cancel['Cancelado'] + np.random.normal(0, 0.02, len(df_cancel)),
                           alpha=0.3, color='#ef4444')
                
                ax2.set_xlabel('Días de anticipación')
                ax2.set_ylabel('Probabilidad de cancelación')
                ax2.set_title('Relación entre días de anticipación y cancelación')
                plt.tight_layout()
                
                buf2 = io.BytesIO()
                plt.savefig(buf2, format='png', dpi=100)
                buf2.seek(0)
                regresion_img = base64.b64encode(buf2.read()).decode('utf-8')
                plt.close(fig2)
                
            except Exception as e:
                logger.error(f"Error en procesamiento: {str(e)}")
                resultado = {'error': f"Error en la predicción: {str(e)}"}
        
        return render_template("prediccion_cancelacion.html",
                            resultado=resultado,
                            datos_usuario=datos_usuario,
                            proba_img=proba_img,
                            regresion_img=regresion_img,
                            motivos=['Trabajo', 'Ocio'],
                            todos_los_paises=todos_los_paises,
                            paises_con_datos=paises_con_datos)
    
    except Exception as e:
        logger.error(f"Error inicial en predicción de cancelación: {str(e)}")
        return render_template("prediccion_cancelacion.html",
                            resultado={'error': f"Error en la predicción: {str(e)}"},
                            datos_usuario={},
                            proba_img=None,
                            regresion_img=None,
                            motivos=['Trabajo', 'Ocio'],
                            todos_los_paises=[],
                            paises_con_datos=[])


@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "data_loaded": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)