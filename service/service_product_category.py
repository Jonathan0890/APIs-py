from config import mysql
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def get_all_product_categories() -> List[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT pc.id_producto_categoria, pc.id_producto, p.nombre AS producto, 
                   pc.id_categoria, c.nombre AS categoria
            FROM productos_categorias pc
            JOIN productos p ON pc.id_producto = p.id_producto
            JOIN categorias c ON pc.id_categoria = c.id_categoria
        """)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener productos_categorias: {e}")
        raise Exception("No se pudieron obtener las relaciones")

def get_product_category_by_id(id_producto_categoria: int) -> Optional[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT pc.id_producto_categoria, pc.id_producto, p.nombre AS producto, 
                   pc.id_categoria, c.nombre AS categoria
            FROM productos_categorias pc
            JOIN productos p ON pc.id_producto = p.id_producto
            JOIN categorias c ON pc.id_categoria = c.id_categoria
            WHERE pc.id_producto_categoria = %s
        """, (id_producto_categoria,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener producto_categoria {id_producto_categoria}: {e}")
        raise Exception("No se pudo obtener la relación solicitada")

def create_product_category(data: Dict) -> int:
    if not data.get('id_producto') or not data.get('id_categoria'):
        raise ValueError("id_producto y id_categoria son requeridos")

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO productos_categorias (id_producto, id_categoria)
            VALUES (%s, %s)
        """, (data['id_producto'], data['id_categoria']))
        mysql.connection.commit()
        return cursor.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al crear producto_categoria: {e}")
        raise Exception("No se pudo crear la relación producto-categoría")

def update_product_category(id_producto_categoria: int, data: Dict) -> bool:
    if not data.get('id_producto') or not data.get('id_categoria'):
        raise ValueError("id_producto y id_categoria son requeridos")

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE productos_categorias
            SET id_producto = %s, id_categoria = %s
            WHERE id_producto_categoria = %s
        """, (data['id_producto'], data['id_categoria'], id_producto_categoria))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al actualizar producto_categoria {id_producto_categoria}: {e}")
        raise Exception("No se pudo actualizar la relación")

def delete_product_category(id_producto_categoria: int) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM productos_categorias WHERE id_producto_categoria = %s", (id_producto_categoria,))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al eliminar producto_categoria {id_producto_categoria}: {e}")
        raise Exception("No se pudo eliminar la relación")
