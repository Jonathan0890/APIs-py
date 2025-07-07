from config import mysql
from extenciones import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

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
    hashed_pw = bcrypt.generate_password_hash(data['contrasena']).decode('utf-8')
    rol = data.get('rol', 'cliente')

    cursor.execute("""
        INSERT INTO clientes (nombre, contrasena, email, direccion, ciudad, estado, pais, rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['nombre'],
        hashed_pw,
        data['email'],
        data.get('direccion', ''),
        data.get('ciudad', ''),
        data.get('estado', ''),
        data.get('pais', ''),
        rol
    ))
    conn.commit()
    return cursor.lastrowid

def update_user(id_cliente, data):
    conn = mysql.connection
    cursor = conn.cursor()
    
    new_password = data.get('contrasena')
    if new_password:
        hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
    else:
        # Si no envían nueva contraseña, dejamos la anterior
        cursor.execute("SELECT contrasena FROM clientes WHERE id_cliente = %s", (id_cliente,))
        hashed_pw = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE clientes
        SET nombre=%s, contrasena=%s, email=%s, direccion=%s, ciudad=%s, estado=%s, pais=%s
        WHERE id_cliente=%s
    """, (
        data['nombre'],
        hashed_pw,
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
    if user:
        column_names = [desc[0] for desc in cursor.description]
        user_data = dict(zip(column_names, user))
        if bcrypt.check_password_hash(user_data['contrasena'], password):
            token = create_access_token(identity=user_data['id_cliente'], expires_delta=timedelta(hours=2))
            return {"user": user_data, "token": token}
    return None
