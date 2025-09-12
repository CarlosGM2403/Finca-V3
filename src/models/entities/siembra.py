from src.models import db
from cultivo import Cultivo

class Siembra(db.Model):
    __tablename__ = 'siembra'

    id_siembra = db.Column(db.Integer, primary_key=True)
    fecha_siembra = db.Column(db.Date, nullable=False)
    detalle = db.Column(db.Text, nullable=False)
    cod_cultivo = db.Column(db.Integer, db.ForeignKey('Cultivos.Id_cultivo'), nullable=False)

    cultivo = db.relationship('Cultivo', backref='siembras')