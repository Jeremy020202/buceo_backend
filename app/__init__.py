from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  
from config import Config
from app.database import db
import os
from flask import send_from_directory 

migrate = Migrate()  

def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads") # Definir carpeta de subida 
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
    os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Crear carpeta si no existe
   

    app.config.from_object(Config)
    CORS(app)

    # Inicializar base de datos
    db.init_app(app)
    migrate.init_app(app, db)  

    from app.routes import routes
    app.register_blueprint(routes)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename) # Servir archivos subidos

    @app.route('/')
    def home():
        return "Servidor Flask conectado a PostgreSQL correctamente ✅"

    return app
