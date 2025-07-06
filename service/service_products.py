from config import mysql
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def get_all_products() -> List[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        products = cursor.fetchall()
        return products
    except Exception as e:
        logger.error(f"Error al obtener productos: {e}")
        raise Exception("No se pudieron obtener los productos")

def get_product_by_id(product_id: int) -> Optional[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (product_id,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener producto {product_id}: {e}")
        raise Exception(f"No se pudo obtener el producto con ID {product_id}")

def create_product(data: Dict) -> int:
    required_fields = ['nombre', 'precio']
    if not all(field in data for field in required_fields):
        raise ValueError("Faltan campos obligatorios: nombre y precio")

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, precio, imagen)
            VALUES (%s, %s, %s, %s)
        """, (
            data['nombre'],
            data.get('descripcion', ''),
            data['precio'],
            data.get('imagen', '')
        ))
        mysql.connection.commit()
        return cursor.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al crear producto: {e}")
        raise Exception("Error al crear el producto")

def update_product(product_id: int, data: Dict) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre = %s,
                descripcion = %s,
                precio = %s,
                imagen = %s
            WHERE id_producto = %s
        """, (
            data.get('nombre'),
            data.get('descripcion'),
            data.get('precio'),
            data.get('imagen'),
            product_id
        ))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al actualizar producto {product_id}: {e}")
        raise Exception(f"No se pudo actualizar el producto con ID {product_id}")

def delete_product(product_id: int) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (product_id,))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al eliminar producto {product_id}: {e}")
        raise Exception(f"No se pudo eliminar el producto con ID {product_id}")
