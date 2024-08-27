from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Caso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(500), nullable=False)
    situacion_problema = db.Column(db.String(5000), nullable=False)
    caracteristicas_de_la_persona = db.Column(db.String(5000), nullable=False)
    
    # Relación con Antecedentes
    antecedentes = relationship("Antecedentes", back_populates="caso", uselist=False)

class Antecedentes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_persona = db.Column(db.String(1000), nullable=False)
    tipo_de_evento_traumatico = db.Column(db.String(5000), nullable=False)
    lugar_del_evento = db.Column(db.String(500), nullable=False)
    edad = db.Column(db.Integer, nullable=True)
    con_quien_vive = db.Column(db.String(1000), nullable=True)
    nivel_de_estudios = db.Column(db.String(500), nullable=True)
    estado_civil = db.Column(db.String(500), nullable=True)
    hobbies = db.Column(db.String(1000), nullable=True)
    
    # Foreign Key
    caso_id = db.Column(db.Integer, db.ForeignKey('caso.id'))
    
    # Relación con Caso
    caso = relationship("Caso", back_populates="antecedentes")
    
