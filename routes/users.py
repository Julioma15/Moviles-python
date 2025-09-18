from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
import datetime
from config.db import get_db_connection
import traceback
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Creamos el blueprint (la ruta)
users_bp = Blueprint('users', __name__)

# inicializar Bcrypt
bcrypt = Bcrypt()


users_bp = Blueprint('users', __name__)

# -------- END POINTS -------------

def validar_campos_requeridos(data, campos):
    faltantes = [campo for campo in campos if not data.get(campo)]
    if faltantes:
        return False, f"ʕ•́ᴥ•̀ʔっ Faltan los siguientes campos: {', '.join(faltantes)}"
    return True, None

@users_bp.route('/register', methods = ["POST"]) #<- Registrar un usuario
def registrar():
    # Obtengo del JSON los datos enviados por el metodo POST por medio del body
    data = request.get_json()
    campos_requeridos = ["nombre", "email", "password"]
    valido, mensaje = validar_campos_requeridos(data, campos_requeridos)
    if not valido:
        return jsonify({"error": mensaje}), 400

    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    #obtenemos la conexion a la base de datos
    cursor = get_db_connection()

    try: 
        # verificar si el usuario ya existe
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error" : "ʕ•́ᴥ•̀ʔっ Ya hay un usuario registrado con ese email"}), 400
        # Hash a la contraseña con Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #insertar el nuevo usuario
        cursor.execute('''INSERT INTO users (nombre, email, password)
                       VALUES (%s, %s, %s)''', 
                       (nombre, email, hashed_password))
        cursor.connection.commit()
        return jsonify({"mensaje" : f"ʕ•́ᴥ•̀ʔっ El usuario {nombre}, [{email}] ha sido creado"})
    
    except Exception as error:
        return jsonify({"error" : f"ʕ•́ᴥ•̀ʔっ Error el registrar el usuario: {str(error)}"}), 500
    
    finally:
        #asegurarse de cerrar la conexion y el cursos a la base de datos despues de la operacion
        cursor.close()

@users_bp.route('/login', methods = ['POST'])
def login():
    data = request.get_json()

    #validar los datos
    campos_requeridos = ["email", "password"]
    valido, mensaje = validar_campos_requeridos(data, campos_requeridos)
    if not valido:
        return jsonify({"error": mensaje}), 400

    email = data.get("email")
    password = data.get("password")

    #obtener la conexion (cursor) a la base de datos usando get_db_connection
    cursor = get_db_connection()
    # consultamos los datos del usuario que se intenta loguear
    cursor.execute("SELECT password, id_usuario FROM users where email = %s", (email,))
    #Obetenemos el hash del password guardado, [hash, id]
    stored_password_hash = cursor.fetchone()
    #cerramos el cursor
    cursor.close()
    #verificamos la contraseña
    if stored_password_hash and bcrypt.check_password_hash(stored_password_hash[0], password):
        #generamos el jwt con duración de 15 minutos
        expires = datetime.timedelta(minutes = 60)
        access_token = create_access_token(
            identity = str(stored_password_hash[1]),
            expires_delta = expires
        )
        return jsonify({"accessToken":access_token}),200
    else:
        return jsonify({"error" : "credenciales incorrectas"}),401
    

@users_bp.route('/datos', methods = ['GET'])
@jwt_required() #<- decorador para requerir el token
def obtener_datos():
    # Obtener la identidad del token
    current_user = get_jwt_identity()
    # Nos conectamos la BD
    cursor = get_db_connection()
    # Vamos a buscar los datos del usuario en la BD
    query = "SELECT id_usuario, nombre, email FROM users WHERE id_usuario = %s"
    cursor.execute(query, (current_user,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        #accedemos a los datos por su indice o posicion
        user_info = {
            "id_ususario" : user_data[0],
            "nombre" : user_data[1],
            "email" : user_data[2]
        }
        return jsonify({"usuario" : user_info}),200
    else:
        return jsonify({"error" : "usuario no encontrado"}),404