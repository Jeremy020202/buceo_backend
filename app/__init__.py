from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Inicializar base de datos
    db.init_app(app)

    from app.routes import routes
    app.register_blueprint(routes)


    @app.route('/')
    def home():
        return "Servidor Flask conectado a PostgreSQL correctamente ✅"

    return app
