from marshmallow import Schema, fields

class InitDialogueSchema(Schema):
    template = fields.String(required=True, description="Template for initializing dialogue")

class SendResponseSchema(Schema):
    response = fields.String(required=True, description="Response from the doctor")
    
    
class NuevoCaso(Schema):
    Nombre=fields.String(required=True, description="Nombre del Caso")
    Lugar_evento=fields.String(required=True, description="Lugar donde ocurre el evento")
    Evento_traumatico=fields.String(required=True, description="Tipo de evento traumatico")
    Situacion_problema=fields.String(required=True, description="Explicacion de la situacion que sufrio la persona")
    Caracteristicas_persona=fields.String(required=True, description="La descripcion de la persona que sufrio el evento")
    Edad=fields.String(required=False, description="Edad del personaje")
    Con_quien_vive=fields.String(required=False, description="Con quien vive el personaje")
    Nivel_estudios=fields.String(required=False, description="Niveles de estudios que tiene el personaje")
    Hobbies=fields.String(required=False, description="Actividades que realiza el personaje")
