from config import mysql
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def get_all_categories() -> List[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categorias")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener categorías: {e}")
        raise Exception("No se pudieron obtener las categorías")

def get_category_by_id(category_id: int) -> Optional[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categorias WHERE id_categoria = %s", (category_id,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener categoría ID {category_id}: {e}")
        raise Exception(f"No se pudo obtener la categoría con ID {category_id}")

def create_category(data: Dict) -> int:
    if not data.get("nombre"):
        raise ValueError("El nombre de la categoría es obligatorio")

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (data['nombre'],))
        mysql.connection.commit()
        return cursor.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al crear categoría: {e}")
        raise Exception("Error al crear la categoría")

def update_category(category_id: int, data: Dict) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE categorias SET nombre = %s WHERE id_categoria = %s",
            (data.get('nombre'), category_id)
        )
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al actualizar categoría ID {category_id}: {e}")
        raise Exception(f"No se pudo actualizar la categoría con ID {category_id}")

def delete_category(category_id: int) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (category_id,))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al eliminar categoría ID {category_id}: {e}")
        raise Exception(f"No se pudo eliminar la categoría con ID {category_id}")
