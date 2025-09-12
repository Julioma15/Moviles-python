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
    email = data.get('email')
    password = data.get('password')

   
    if not email or not password:  
        return jsonify({"error": mensaje}), 400
    cursor = get_db_connection()

#consultar datos del usuario en la base de datos
    cursor.execute("SELECT password, id_usuario FROM users WHERE email = %s", (email,))
    store_password_hash = cursor.fetchone()
    cursor.close()

    if store_password_hash and bcrypt.check_password_hash(store_password_hash[0], password):
        # Crear el token JWT duración 90 minutos
        expires = datetime.timedelta(minutes=90)
        access_token = create_access_token(
            identity={"email": email, "id_usuario": store_password_hash[1]},
            expires_delta=expires
        )
        return jsonify({"token": access_token}), 200
    else:
        return jsonify({"error": "ʕ•́ᴥ•̀ʔっ Credenciales inválidas"}), 401
@users_bp.route('/datos', methods = ['GET'])
@jwt_required()
def obtener_datos_usuario():
    current_user = get_jwt_identity()
    user_id = current_user["id_usuario"]
    cursor = get_db_connection()
    query = "SELECT id_usuario, nombre, email FROM users WHERE id_usuario = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return jsonify({
            "id_usuario": user_data[0],
            "nombre": user_data[1],
            "email": user_data[2]
        })
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

# No hace nada aun:
#Crear un endpoint usando el PUT y pasando datos por el body y el URL
@users_bp.route('/editar/<int:user_id>', methods = ['PUT'])
def editar(user_id):
    #obtenemos los datos de body
    data = request.get_json()
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    mensaje = f" ʕ•́ᴥ•̀ʔっ El usuario {nombre} {apellido} con ID: {user_id} ha sido modificado correctamente."
    return  jsonify({"mensaje": mensaje})