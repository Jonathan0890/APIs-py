from config import mysql
from datetime import datetime

def get_carrito_by_cliente(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id_carrito, c.id_producto, p.nombre, p.precio, c.cantidad,
               (p.precio * c.cantidad) AS subtotal, c.fecha_agregado,
                c.descuento_aplicado
        FROM carrito c
        JOIN productos p ON c.id_producto = p.id_producto
        WHERE c.id_cliente = %s
    """, (id_cliente,))
    rows = cursor.fetchall()

    if not rows:
        return None

    column_names = [desc[0] for desc in cursor.description]
    carrito = [dict(zip(column_names, row)) for row in rows]
    
    # Total general
    total = sum(item['subtotal'] for item in carrito)
    return {"items": carrito, "total": round(total, 2)}

def add_producto_al_carrito(data):
    conn = mysql.connection
    cursor = conn.cursor()

    id_cliente = data['id_cliente']
    id_producto = data['id_producto']
    cantidad = data.get('cantidad', 1)
    descuento = data.get('descuento_aplicado', 0)

    cursor.execute("""
        SELECT cantidad FROM carrito 
        WHERE id_cliente = %s AND id_producto = %s
    """, (id_cliente, id_producto))
    row = cursor.fetchone()

    if row:
        nueva_cantidad = row[0] + cantidad
        cursor.execute("""
            UPDATE carrito 
            SET cantidad = %s, fecha_agregado = %s 
            WHERE id_cliente = %s AND id_producto = %s
        """, (nueva_cantidad, datetime.now(), id_cliente, id_producto))
    else:
        cursor.execute("""
            INSERT INTO carrito (id_cliente, id_producto, cantidad, fecha_agregado, descuento_aplicado)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, id_producto, cantidad, datetime.now(), descuento))

    conn.commit()

def update_cantidad_carrito(id_carrito, cantidad):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE carrito
        SET cantidad = %s, fecha_agregado = %s
        WHERE id_carrito = %s
    """, (cantidad, datetime.now(), id_carrito))
    conn.commit()

def delete_producto_carrito(id_carrito):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito WHERE id_carrito = %s", (id_carrito,))
    conn.commit()

def vaciar_carrito_cliente(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
