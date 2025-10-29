import os

class Config:
    # Configuración de la base de datos
    DB_NAME = "buceo_db"
    DB_USER = "postgres"
    DB_PASSWORD = "UTP123" 
    DB_HOST = "localhost"
    DB_PORT = "5432"

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
