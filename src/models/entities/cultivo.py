from src.models import db

class Cultivo(db.Model):
    __tablename__ = 'Cultivos'

    Id_cultivo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False)