from flask import Flask
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from config.db import init_db

#importar la ruta del blueprint
from routes.tareas import tareas_bp
from routes.users import users_bp

#cargar las variables de entorno desde el archivo .env
load_dotenv()

#Funcion para crear la app
def create_app():

    # instanciamos la app
    app = Flask(__name__) #instanciamos la app
    init_db(app) # configura la base de datos
    app.config['JWT_SECRET_KEY']  = os.getenv("JWT_SECRET_KEY") #configuramos el secreto JWT desde .env
    jwt = JWTManager(app) #vamos a usar JWT

    #registramos el blueprint
    app.register_blueprint(tareas_bp, url_prefix = '/tareas') 
    app.register_blueprint(users_bp, url_prefix = '/users')

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080)) #obtenemos el puerto
    app.run(host="0.0.0.0", port = port, debug = True)