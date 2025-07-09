from config import mysql
from datetime import datetime
from utils.ia_helper import analizar_sentimiento_resena

def get_all_resenas():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resenas")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]

def get_resena_by_id(id_resena):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resenas WHERE id_resena = %s", (id_resena,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        return dict(zip(column_names, row))
    return None

def create_resena(data):
    conn = mysql.connection
    cursor = conn.cursor()
    sentimiento = analizar_sentimiento_resena(data['comentario']) if 'comentario' in data else 'Sin comentario'
    
    cursor.execute("""
        INSERT INTO resenas (id_producto, id_cliente, calificacion, comentario, fecha, sentimiento)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['id_producto'],
        data['id_cliente'],
        data['calificacion'],
        data.get('comentario'),
        datetime.now(),
        sentimiento
    ))
    conn.commit()

def update_resena(id_resena, data):
    conn = mysql.connection
    cursor = conn.cursor()
    update_fields = []
    update_values = []

    if 'calificacion' in data:
        update_fields.append("calificacion = %s")
        update_values.append(data['calificacion'])
    if 'comentario' in data:
        update_fields.append("comentario = %s")
        update_values.append(data['comentario'])

    update_fields.append("fecha = %s")
    update_values.append(datetime.now())

    update_values.append(id_resena)

    cursor.execute(f"""
        UPDATE resenas
        SET {', '.join(update_fields)}
        WHERE id_resena = %s
    """, update_values)
    conn.commit()

def delete_resena(id_resena):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resenas WHERE id_resena = %s", (id_resena,))
    conn.commit()
