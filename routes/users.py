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

# Creamos el blueprint
users_bp = Blueprint('users', __name__)

# inicializar Bcrypt
bcrypt = Bcrypt()


users_bp = Blueprint('users', __name__)

# -------- END POINTS -------------

@users_bp.route('/register', methods = ["POST"]) #<- Registrar un usuario
def registrar():
    # Obtengo del JSON los datos enviados por el metodo POST
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not nombre or not  email or not password:
        return jsonify({"error" : "Porfavor llena todos los campos"}), 400

    #obtenemos la conexion a la base de datos
    cursor = get_db_connection()

    try: 
        # verificar si el usuario ya existe
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error" : "Este usuario ya existe"}), 400
        # Hash a la contraseña con Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #insertar el nuevo usuario
        cursor.execute('''INSERT INTO users (nombre,  email, password)
                       VALUES (%s, %s, %s)''', 
                       (nombre, email, hashed_password))
        cursor.connection.commit()
        return jsonify({"mensaje" : f"El usuario {nombre} ha sido creado"})
    
    except Exception as e:
        return jsonify({"error" : f"Error el registrar el usuario: {str(e)}"}), 500
    
    finally:
        #asegurarse de cerrar la conexion y el cursos a la base de datos despues de la operacion
        cursor.close()
        




# Obtener datos
@users_bp.route('/datos', methods = ['GET']) #<- obtener lo datos
def obtener_datos():
    return jsonify({"mensaje" : "Hola mundo!"})