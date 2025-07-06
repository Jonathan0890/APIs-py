import os
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos usando variables de entorno
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'product_db')

# Configuración adicional de Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

mysql = MySQL(app)