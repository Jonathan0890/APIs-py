from config import mysql
from flask_jwt_extended import create_access_token
from flask import current_app
from extenciones import bcrypt
from utils.slack_helper import notificar_slack
from utils.email_helper import enviar_correo_otp
import requests
from datetime import timedelta
import random

def autenticar_usuario(email, contrasena):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        columns = [desc[0] for desc in cursor.description]
        user_data = dict(zip(columns, user))

        if bcrypt.check_password_hash(user_data['contrasena'], contrasena):
            # Slack alerta
            notificar_slack(f"✅ Login exitoso para {email}")

            # Correo OTP
            otp = generar_codigo_otp()
            enviar_correo_otp(email, otp)
            
            # Token JWT
            token = create_access_token(identity=user_data['id_cliente'], expires_delta=timedelta(hours=1))
            return {"token": token, "user": user_data, "otp_enviado": True}
        else:
            return None
    return None


# Generar código OTP
def generar_codigo_otp():
    return str(random.randint(100000, 999999))

