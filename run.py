from app import create_app
from app.database import db
from app.models import Equipo


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # 👈 elimina las tablas existentes
        db.create_all()  # 👈 crea las tablas en la base de datos
    app.run(debug=True)
