from config import mysql
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def get_all_detalles() -> List[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM detalles_pedido")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener detalles: {e}")
        raise Exception("No se pudieron obtener los detalles del pedido")

def get_detalle_by_id(id_detalle: int) -> Optional[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM detalles_pedido WHERE id_detalle = %s", (id_detalle,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener detalle ID {id_detalle}: {e}")
        raise Exception("No se pudo obtener el detalle del pedido")

def create_detalle(data: Dict) -> int:
    required_fields = ['id_pedido', 'id_producto', 'cantidad', 'precio_unitario']
    if not all(field in data for field in required_fields):
        raise ValueError("Todos los campos (id_pedido, id_producto, cantidad, precio_unitario) son obligatorios")
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (
            data['id_pedido'],
            data['id_producto'],
            data['cantidad'],
            data['precio_unitario']
        ))
        mysql.connection.commit()
        return cursor.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al crear detalle: {e}")
        raise Exception("No se pudo crear el detalle del pedido")

def update_detalle(id_detalle: int, data: Dict) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE detalles_pedido
            SET id_pedido = %s, id_producto = %s, cantidad = %s, precio_unitario = %s
            WHERE id_detalle = %s
        """, (
            data.get('id_pedido'),
            data.get('id_producto'),
            data.get('cantidad'),
            data.get('precio_unitario'),
            id_detalle
        ))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al actualizar detalle ID {id_detalle}: {e}")
        raise Exception("No se pudo actualizar el detalle del pedido")

def delete_detalle(id_detalle: int) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM detalles_pedido WHERE id_detalle = %s", (id_detalle,))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al eliminar detalle ID {id_detalle}: {e}")
        raise Exception("No se pudo eliminar el detalle del pedido")
