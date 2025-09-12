from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv
from flask_mysqldb import MySQL
from config.db import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
load_dotenv()
mysql = MySQL()

#creamos el blueprint
tareas_bp = Blueprint('tareas', __name__)

#creamos un endpoint para obtener tareas
@tareas_bp.route('/obtener', methods = ['GET'])
def get():
    return jsonify({"mensaje" : "ʕ•́ᴥ•̀ʔっ Estas son su tareas: "})

def validar_campos_requeridos(data, campos):
    faltantes = [campo for campo in campos if not data.get(campo)]
    if faltantes:
        return False, f"ʕ•́ᴥ•̀ʔっ Faltan los siguientes campos: {', '.join(faltantes)}"
    return True, None

#creamos un endpoint POST, recibe datos desde el body
@tareas_bp.route('/addTarea', methods = ['POST'])
def add():
    #Obtenemos los datos del body
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        descripcion = data.get('descripcion')
        if not descripcion:
           return jsonify({"error": "ʕ•́ᴥ•̀ʔっ La descripción es requerida"}), 400
        cursor = get_db_connection()
        query = "INSERT INTO tareas (descripcion, id_usuario) VALUES (%s, %s)"
        cursor.execute(query, (descripcion, current_user['id_usuario']))
        cursor.connection.commit()
        return jsonify({"mensaje" : f"ʕ•́ᴥ•̀ʔっ Tu tarea: {descripcion}, ha sido creada"}), 200
    except Exception as error:  # <-- CORREGIDO
        return jsonify({"error" : f"ʕ•́ᴥ•̀ʔっ No se pudo crear la tarea: {str(error)}"})
    finally:
        cursor.close()

@jwt_required()
def obtener_tareas():
    current_user = get_jwt_identity()
    cursor = get_db_connection()
    query = '''
               SELECT a.id_tarea, a.descripcion, b.nombre, b.email, a.creado_en
               FROM tareas as a 
               INNER JOIN users as b on a.id_usuario = b.id_usuario 
               WHERE a.id_usuario = %s;
            '''
    cursor.execute(query, (current_user,))
    lista = cursor.fetchall()
    cursor.close()
    if not lista:
        return jsonify({"mensaje": "ʕ•́ᴥ•̀ʔっ No tienes tareas creadas"}), 200
    else:
        return jsonify(lista), 200

@tareas_bp.route('/update/<int:tarea_id>', methods=['PUT'])
def actualizar_tarea(tarea_id):
    data = request.get_json()
    descripcion = data.get('descripcion')
    if not descripcion:
        return jsonify({"error": "ʕ•́ᴥ•̀ʔっ La descripción es requerida"}), 400
    cursor = get_db_connection()
    query = "UPDATE tareas SET descripcion = %s WHERE id_tarea = %s"
    cursor.execute(query, (descripcion, tarea_id))
    tarea_existe=cursor.fetchone()
    if not tarea_existe:
        cursor.close()
        return jsonify({"error": "ʕ•́ᴥ•̀ʔっ La tarea no existe"}), 404
    if not tarea_existe[1] == int(current_user):
        cursor.close()
        return jsonify({"error": "ʕ•́ᴥ•̀ʔっ No tienes permiso para actualizar esta tarea"}), 403
    try:
        cursor.execute(query, (descripcion, tarea_id))
        cursor.connection.commit()
        return jsonify({"mensaje": f"ʕ•́ᴥ•̀ʔっ La tarea {tarea_id} ha sido actualizada"}), 200
    except Exception as e:
        return jsonify({"error": f"ʕ•́ᴥ•̀ʔっ Error al actualizar la tarea: {str(e)}"}), 500
    finally:
        cursor.close()