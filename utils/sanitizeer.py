import bleach

def sanitize_string(value):
    """Sanitiza una cadena eliminando HTML/script peligrosos."""
    if isinstance(value, str):
        return bleach.clean(value)
    return value

def sanitize_dict(data):
    """Sanitiza todos los campos de un diccionario."""
    if not isinstance(data, dict):
        return data
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_string(v) if isinstance(v, str) else v for v in value]
        else:
            sanitized[key] = value
    return sanitized
