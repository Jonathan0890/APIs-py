import smtplib
from email.message import EmailMessage
import os

def enviar_correo_otp(destinatario, codigo_otp):
    remitente = os.getenv('EMAIL_FROM')
    clave = os.getenv('EMAIL_PASSWORD')

    if not remitente or not clave:
        print("❌ No se configuró EMAIL_FROM o EMAIL_PASSWORD en .env")
        return False

    try:
        mensaje = EmailMessage()
        mensaje['Subject'] = 'Tu código OTP'
        mensaje['From'] = remitente
        mensaje['To'] = destinatario
        mensaje.set_content(f'Tu código de verificación es: {codigo_otp}')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, clave)
            smtp.send_message(mensaje)

        print("✅ Código OTP enviado correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")
        return False
