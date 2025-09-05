from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

# cargamos las vairables de entorno
load_dotenv()

# inicializamos Flask_MySQL
mysql =  MySQL()

# configuramos el acceso a nuestra base de datos
def init_db(app):
    """Configurar la base de datos con la instancia de Flask"""
    app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
    app.config['MYSQL_USER'] = os.getenv("DB_USER")
    app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
    app.config['MYSQL_DB'] = os.getenv("DB_NAME")
    app.config['MYSQL_PORT'] = int(os.getenv("DB_PORT"))
    mysql.init_app(app)

# Funcion para obtener el cursor a la base de datos
#el cursos recorre la base de datos
def get_db_connection():
    '''Devuelve un cursor para interacruar con la base de datos'''
    try:
        connection = mysql.connection
        return connection.cursor()
    except Exception as error:
        raise RuntimeError(f"Error al conectar a la base de datos: {error}")