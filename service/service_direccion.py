from config import mysql

def get_all_direcciones():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM direcciones")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]

def get_direccion_by_id(id_direccion):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM direcciones WHERE id_direccion = %s", (id_direccion,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        return dict(zip(column_names, row))
    return None

def create_direccion(data):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO direcciones (id_cliente, calle, ciudad, estado, codigo_postal, pais)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['id_cliente'],
        data.get('calle'),
        data.get('ciudad'),
        data.get('estado'),
        data['codigo_postal'],
        data.get('pais')
    ))
    conn.commit()

def update_direccion(id_direccion, data):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE direcciones
        SET id_cliente = %s, calle = %s, ciudad = %s, estado = %s, codigo_postal = %s, pais = %s
        WHERE id_direccion = %s
    """, (
        data['id_cliente'],
        data.get('calle'),
        data.get('ciudad'),
        data.get('estado'),
        data['codigo_postal'],
        data.get('pais'),
        id_direccion
    ))
    conn.commit()

def delete_direccion(id_direccion):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM direcciones WHERE id_direccion = %s", (id_direccion,))
    conn.commit()
