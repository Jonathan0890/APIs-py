from config import mysql
from datetime import datetime

def obtener_todos_cupones():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cupones")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]

def crear_cupon(codigo, descuento, valido_hasta):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cupones (codigo, descuento, valido_hasta)
        VALUES (%s, %s, %s)
    """, (codigo, descuento, valido_hasta))
    conn.commit()

def validar_cupon(codigo):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM cupones 
        WHERE codigo = %s AND valido_hasta >= CURDATE()
    """, (codigo,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        return dict(zip(column_names, row))
    return None

def eliminar_cupon(id_cupon):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cupones WHERE id_cupon = %s", (id_cupon,))
    conn.commit()

def registrar_uso_cupon(id_cupon):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cupones SET usos_actuales = usos_actuales + 1
        WHERE id_cupon = %s
    """, (id_cupon,))
    conn.commit()
