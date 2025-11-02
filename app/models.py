from app.database import db

class Equipo(db.Model):
    __tablename__ = 'equipos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    fecha_compra = db.Column(db.Date)
    periodo_mantenimiento = db.Column(db.String(50))
    imagen_url = db.Column(db.String(255))
    estado = db.Column(db.String(50))
    proximo_mantenimiento = db.Column(db.Date)
    ultimo_mantenimiento = db.Column(db.Date)


    def __repr__(self):
        return f'<Equipo {self.nombre}>'

class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    agente = db.Column(db.String(100))
    descripcion = db.Column(db.String(200))
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)

    equipo = db.relationship('Equipo', backref=db.backref('mantenimientos', lazy=True))

    def __repr__(self):
        return f'<Mantenimiento {self.tipo} - Equipo {self.equipo_id}>'
