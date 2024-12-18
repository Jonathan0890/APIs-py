from config import mysql

def get_all_products():
    """
    Obtiene todos los productos de la base de datos.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return products
    except Exception as e:
        raise Exception(f"Error al obtener productos: {e}")

def get_product_by_id(product_id):
    """
    Obtiene un producto por su ID.
    
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        return product
    except Exception as e:
        raise Exception(f"Error al obtener el producto con ID {product_id}: {e}")

def create_product(data):
    """
    Crea un nuevo producto en la base de datos.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, price, category, description)
            VALUES (%s, %s, %s, %s)
        """, (data['name'], data['price'], data['category'], data['description']))
        conn.commit()
        return cursor.lastrowid  # Devuelve el ID del nuevo producto
    except Exception as e:
        raise Exception(f"Error al crear el producto: {e}")

def update_product(product_id, data):
    """
    Actualiza un producto existente.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products
            SET name = %s, price = %s, category = %s, description = %s
            WHERE id = %s
        """, (data['name'], data['price'], data['category'], data['description'], product_id))
        conn.commit()
        return cursor.rowcount  # Número de filas afectadas
    except Exception as e:
        raise Exception(f"Error al actualizar el producto con ID {product_id}: {e}")

def delete_product(product_id):
    """
    Elimina un producto por su ID.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        return cursor.rowcount  # Número de filas eliminadas
    except Exception as e:
        raise Exception(f"Error al eliminar el producto con ID {product_id}: {e}")
