from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import os
from dotenv import load_dotenv
from flask_mysqldb import MySQL
from config.db import get_db_connection

load_dotenv()
mysql = MySQL()

#creamos el blueprint
tareas_bp = Blueprint('tareas', __name__)

def validar_campos_requeridos(data, campos):
    faltantes = [campo for campo in campos if not data.get(campo)]
    if faltantes:
        return False, f"ʕ•́ᴥ•̀ʔっ Faltan los siguientes campos: {', '.join(faltantes)}"
    return True, None

# ------ ENDPOINTS -------

#creamos un endpoint para obtener tareas de un usuario en especifico
@tareas_bp.route('/obtener', methods=['GET'])
@jwt_required()
def obtener_tareas():
    current_user = get_jwt_identity()
    cursor = get_db_connection()
    query = '''
               SELECT a.id_tarea, a.descripcion, b.nombre, b.email, a.creadoEn
               FROM tareas as a 
               INNER JOIN users as b on a.id_usuario = b.id_usuario 
               WHERE a.id_usuario = %s;
            '''
    cursor.execute(query, (current_user,))
    lista = cursor.fetchall()
    cursor.close()
    if not lista:
        return jsonify({"error": "Este usuario no tiene tareas"}), 400
    else:
        return jsonify({"lista": lista}), 200
   




#creamos un endpoint POST, recibe datos desde el body
@tareas_bp.route('/crear', methods = ['POST'])
@jwt_required()
def crear():
    #Obtenemos los datos del body
    data = request.get_json()
    campos_requeridos = ["descripcion"]
    valido, mensaje = validar_campos_requeridos(data, campos_requeridos)
    if not valido:
        return jsonify({"error": mensaje}), 400
    
    try:
        #obtener la identidad del token (id_usuario)
        current_user = get_jwt_identity()
        #obtenemos los datos del body
        data = request.get_json()
        descripcion = data.get('descripcion')

        cursor = get_db_connection()
        #guardamos la tarea
        query = 'INSERT INTO tareas (descripcion, id_usuario) VALUES (%s, %s)'
        cursor.execute(query, (descripcion, current_user))
        cursor.connection.commit()
        return jsonify({"mensaje" : f"ʕ•́ᴥ•̀ʔっ User_id: [{current_user}] Tu tarea: {descripcion}, ha sido creada"}), 200
    except Exception as error:
        return jsonify({"error" : f"ʕ•́ᴥ•̀ʔっ No se pudo crear la tarea: {str(error)}"}),500
    finally:
        cursor.close()

@tareas_bp.route('/update/<int:id_tarea>', methods = ['PUT'])
@jwt_required()
def actualizar(id_tarea):
    #obtener la identidad del usuario del jwt
    current_usuer = get_jwt_identity()
    #obtenemos los datos del body
    data = request.get_json()
    descripcion = data.get('descripcion')
    if not descripcion:
        return jsonify({"error" : "Debes proporcionar la descripción"}), 400
    #obtenemos la conexion
    cursor = get_db_connection()
    #verificamos que la trea exista y que el usuario loguado esel dueño de la tarea
    cursor.execute("SELECT * FROM tareas WHERE id_tarea = %s", (id_tarea,))
    tarea_existe = cursor.fetchone()
    if not tarea_existe:
        cursor.close()
        return jsonify({"error" : "La tarea no existe"}), 404
    if not tarea_existe[1] == int(current_usuer):
        cursor.close()
        return jsonify({"error" : "Usiario no autorizado"}), 401
    #Actualizar los datos
    try: 
        cursor.execute('UPDATE tareas SET descripcion = %s WHERE id_tarea = %s', (descripcion, id_tarea))
        cursor.connection.commit()
        return jsonify({"Mensaje" : "Datos actualizados correctamemte"}),200
    except Exception as error:
        return jsonify({"error" : f"Error al actualizar los datos: {str(error)}"}), 500
    finally:
        cursor.close()


@tareas_bp.route('/delete/<int:id_tarea>', methods=['DELETE'])
@jwt_required()
def borrar(id_tarea):
    # obtener la identidad del usuario del jwt
    current_user = get_jwt_identity()
    cursor = get_db_connection()
    # verificamos que la tarea exista y que el usuario logueado es el dueño de la tarea
    cursor.execute("SELECT * FROM tareas WHERE id_tarea = %s", (id_tarea,))
    tarea_existe = cursor.fetchone()
    if not tarea_existe:
        cursor.close()
        return jsonify({"error": "La tarea no existe"}), 404
    if not tarea_existe[1] == int(current_user):
        cursor.close()
        return jsonify({"error": "Usuario no autorizado"}), 401
    # Eliminar la tarea
    try:
        cursor.execute('DELETE FROM tareas WHERE id_tarea = %s', (id_tarea,))
        cursor.connection.commit()
        return jsonify({"Mensaje": "Tarea eliminada correctamente"}), 200
    except Exception as error:
        return jsonify({"error": f"Error al eliminar la tarea: {str(error)}"}), 500
    finally:
        cursor.close()