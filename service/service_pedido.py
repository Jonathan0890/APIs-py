from config import mysql
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def get_all_pedidos() -> List[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pedidos")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al obtener pedidos: {e}")
        raise Exception("No se pudieron obtener los pedidos")

def get_pedido_by_id(id_pedido: int) -> Optional[Dict]:
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error al obtener pedido {id_pedido}: {e}")
        raise Exception("No se pudo obtener el pedido solicitado")

def create_pedido(data: Dict) -> int:
    if not data.get('id_cliente') or not data.get('total'):
        raise ValueError("id_cliente y total son campos obligatorios")
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pedidos (id_cliente, total)
            VALUES (%s, %s)
        """, (data['id_cliente'], data['total']))
        mysql.connection.commit()
        return cursor.lastrowid
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al crear pedido: {e}")
        raise Exception("No se pudo crear el pedido")

def update_pedido(id_pedido: int, data: Dict) -> bool:
    if not data.get('id_cliente') or not data.get('total'):
        raise ValueError("id_cliente y total son campos obligatorios")
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pedidos 
            SET id_cliente = %s, total = %s
            WHERE id_pedido = %s
        """, (data['id_cliente'], data['total'], id_pedido))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al actualizar pedido {id_pedido}: {e}")
        raise Exception("No se pudo actualizar el pedido")

def delete_pedido(id_pedido: int) -> bool:
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        mysql.connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        mysql.connection.rollback()
        logger.error(f"Error al eliminar pedido {id_pedido}: {e}")
        raise Exception("No se pudo eliminar el pedido")
