from config import mysql
from datetime import datetime

def get_all_pagos():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pagos")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]

def get_pago_by_id(id_pago):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pagos WHERE id_pago = %s", (id_pago,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        return dict(zip(column_names, row))
    return None

def create_pago(data):
    conn = mysql.connection
    cursor = conn.cursor()
    fecha_pago = datetime.now()
    cursor.execute("""
        INSERT INTO pagos (id_pedido, metodo_pago, estado_pago, fecha_pago, comprobante)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['id_pedido'],
        data['metodo_pago'],
        data.get('estado_pago', 'pendiente'),
        fecha_pago,
        data.get('comprobante')  # opcional
    ))
    conn.commit()
    return cursor.lastrowid

def update_pago(id_pago, data):
    conn = mysql.connection
    cursor = conn.cursor()
    update_fields = []
    update_values = []

    if 'metodo_pago' in data:
        update_fields.append("metodo_pago = %s")
        update_values.append(data['metodo_pago'])
    if 'estado_pago' in data:
        update_fields.append("estado_pago = %s")
        update_values.append(data['estado_pago'])
        update_fields.append("fecha_pago = %s")
        update_values.append(datetime.now())
    if 'comprobante' in data:
        update_fields.append("comprobante = %s")
        update_values.append(data['comprobante'])

    if not update_fields:
        return 0

    update_values.append(id_pago)
    cursor.execute(f"""
        UPDATE pagos
        SET {', '.join(update_fields)}
        WHERE id_pago = %s
    """, update_values)
    conn.commit()
    return cursor.rowcount

def delete_pago(id_pago):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pagos WHERE id_pago = %s", (id_pago,))
    conn.commit()
    return cursor.rowcount
