from config import mysql
import bcrypt

def get_all_users():
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]

def get_user_by_id(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
    row = cursor.fetchone()
    if row:
        column_names = [desc[0] for desc in cursor.description]
        return dict(zip(column_names, row))
    return None

def create_user(data):
    conn = mysql.connection
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(data['contrasena'].encode('utf-8'), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO clientes (nombre, contrasena, email, direccion, ciudad, estado, pais)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['nombre'],
        hashed_pw,
        data['email'],
        data.get('direccion', ''),
        data.get('ciudad', ''),
        data.get('estado', ''),
        data.get('pais', '')
    ))
    conn.commit()
    return cursor.lastrowid

def update_user(id_cliente, data):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET nombre=%s, contrasena=%s, email=%s, direccion=%s, ciudad=%s, estado=%s, pais=%s
        WHERE id_cliente=%s
    """, (
        data['nombre'],
        data['contrasena'],
        data['email'],
        data['direccion'],
        data['ciudad'],
        data['estado'],
        data['pais'],
        id_cliente
    ))
    conn.commit()
    return cursor.rowcount

def delete_user(id_cliente):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    return cursor.rowcount

def login_user(email, password):
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):  # columna 2 = contrasena
        return user
    return None
