import requests
from flask import current_app

def notificar_slack(mensaje):
    webhook_url = current_app.config.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return False
    try:
        response = requests.post(webhook_url, json={"text": mensaje})
        return response.status_code == 200
    except Exception as e:
        print(f"[Slack] Error al enviar notificación: {e}")
        return False
