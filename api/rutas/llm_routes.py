from flask_smorest import Blueprint 
from modelos.funcs import Nuevo_Caso
from flask_cors import cross_origin
from schemas.request_schemas import InitDialogueSchema, SendResponseSchema , NuevoCaso
from modelos.llm import Dialogue, CustomAgent
from modelos.documents import Document
from flask import jsonify, render_template, request, jsonify, Response , redirect , url_for
import re
from casos.models import Caso, db , Antecedentes
import json

conversation_agent = CustomAgent()
conversation_agent.addSystemPrompt("""
You are an expert in generating a psychiatric patient's response based on what the doctor tells them.

You must respond to the doctor based on the last thing he tells you, try not to repeat the patient's previous responses.

The patient must answer following all the instructions given by the psychiatrist.

You should always generate the response following the following format and in Spanish

"speaker":
"text":


""")

class LLM_Routes():
    llm_bp = []
    dialogue = None
    
    def NuevoCaso(self):
        simple_page = Blueprint("NuevoCaso", __name__)

        @simple_page.route("/NuevoCaso", methods=["POST"])
        @cross_origin()
        def f():
            data = request.form.to_dict()  # Convertir los datos del formulario a un diccionario

            # Crear entrada en Antecedentes
            antecedentes = Antecedentes(
                nombre_persona=data["nombre"],
                tipo_de_evento_traumatico=data["tipo_evento"],
                lugar_del_evento=data["lugar"],
                edad=data["edad"],
                con_quien_vive=data["con_quien_vive"],
                nivel_de_estudios=data["nivel_estudios"],
                estado_civil=data["estado_civil"],
                hobbies=data["hobbies"]
            )
            db.session.add(antecedentes)
            db.session.commit()

            antecedentes_str = ", ".join([f"{key}={value}" for key, value in data.items()])
            response = Nuevo_Caso(antecedentes_str)

            # Separar la respuesta en 'situacion_problema' y 'caracteristicas_de_la_persona'
            situacion_problema = re.search(r'situacion_problema=(.*?)(?=caracteristicas_de_la_persona=)', response, re.DOTALL).group(1).strip()
            caracteristicas_de_la_persona = re.search(r'caracteristicas_de_la_persona=(.*)', response, re.DOTALL).group(1).strip()

            # Crear entrada en Caso y enlazar con Antecedentes
            caso = Caso(
                nombre=data["nombre"],
                situacion_problema=situacion_problema,
                caracteristicas_de_la_persona=caracteristicas_de_la_persona,
                antecedentes=antecedentes
            )
            db.session.add(caso)
            db.session.commit()

            # Preparar la respuesta JSON con los datos del caso creado
            caso_creado = {
                "nombre": caso.nombre,
                "situacion_problema": caso.situacion_problema,
                "caracteristicas_de_la_persona": caso.caracteristicas_de_la_persona
            }

            return redirect(url_for('panel.f'))

        self.llm_bp.append(simple_page)


    def sendResponse(self):
        simple_page = Blueprint("sendResponse", __name__)
        @simple_page.route("/sendResponse", methods = ["POST"])
        @cross_origin()
        def f():
            msg = request.json["response"]
            response = self.dialogue.getNextResponse(doctor_answer=msg)
            return jsonify({"response": response}),200
        self.llm_bp.append(simple_page)


    def initDialogue(self):
        simple_page = Blueprint("initDialogue", __name__)

        @simple_page.route("/initDialogue", methods=["POST"])
        @cross_origin()
        @simple_page.arguments(InitDialogueSchema, location="json")
        def f(args):
            template = args["template"]
            caso = Caso.query.filter_by(nombre=template).first()
            if caso:
                patient_params = {
                    "contexto_para_participantes": caso.situacion_problema,
                    "descripcion_personaje": caso.caracteristicas_de_la_persona
                }
                self.dialogue = Dialogue(agent=conversation_agent, patient_params=patient_params)
                return jsonify({"response": "Diálogo iniciado con éxito"}), 200
            return jsonify({"error": "Caso no encontrado"}), 404

        self.llm_bp.append(simple_page)
        print(f"Blueprint created: {simple_page.name} for /initDialogue")
        
        
    def getCaseInfo(self):
        case_info_page = Blueprint("getCaseInfo", __name__)

        @case_info_page.route("/getCaseInfo", methods=["GET"])
        @cross_origin()
        def get_case_info():
            if self.dialogue:
                # Aquí asumimos que tienes acceso a self.dialogue desde tu instancia actual
                caso_actual = self.dialogue.patient_params
                return jsonify({
                    "contexto_para_participantes": caso_actual["contexto_para_participantes"],
                    "descripcion_personaje": caso_actual["descripcion_personaje"]
                }), 200
            else:
                return jsonify({"error": "No se ha iniciado ningún diálogo"}), 404

        self.llm_bp.append(case_info_page)
        print(f"Blueprint created: {case_info_page.name} for /getCaseInfo")



    def getFiles(self):
        simple_page = Blueprint("getFiles", __name__)
        @simple_page.route("/getFiles", methods=["GET"])
        @cross_origin()
        def f():
            casos = Caso.query.all()
            response = [{"contexto_para_participantes": caso.contexto_para_participantes, "descripcion_personaje": caso.descripcion_personaje} for caso in casos]
            return jsonify({"response": response}), 200
        self.llm_bp.append(simple_page)
        print(f"Blueprint created: {simple_page.name} for /getFiles")
        
        
    def getAntecedentesById(self):
        simple_page = Blueprint("getAntecedentesById", __name__)
        @simple_page.route("/antecedentes/<int:caso_id>", methods=["GET"])
        @cross_origin()
        def f(caso_id):
            caso = Caso.query.get(caso_id)
            if caso:
                antecedentes = caso.antecedentes
                if antecedentes:
                    return jsonify({
                        "id": antecedentes.id,
                        "nombre_persona": antecedentes.nombre_persona,
                        "tipo_de_evento_traumatico": antecedentes.tipo_de_evento_traumatico,
                        "lugar_del_evento": antecedentes.lugar_del_evento,
                        "edad": antecedentes.edad,
                        "con_quien_vive": antecedentes.con_quien_vive,
                        "nivel_de_estudios": antecedentes.nivel_de_estudios,
                        "estado_civil": antecedentes.estado_civil,
                        "hobbies": antecedentes.hobbies
                    }), 200
                else:
                    return jsonify({"message": "El caso no tiene antecedentes asociados"}), 404
            else:
                return jsonify({"error": "Caso no encontrado"}), 404
        self.llm_bp.append(simple_page)
        print(f"Blueprint created: {simple_page.name} for /antecedentes/<int:caso_id>")

    def panel(self):
        simple_page = Blueprint("panel", __name__)
        @simple_page.route("/", methods=["GET"])
        @cross_origin()
        def f():
            casos =  Caso.query.order_by(Caso.id.desc()).all()
            antecedentes = Antecedentes.query.all()
            return render_template("panel.html", casos=casos, antecedentes=antecedentes)
        self.llm_bp.append(simple_page)
        print(f"Blueprint created: {simple_page.name} for /")
        
    
    def eliminar_caso(self):
        simple_page = Blueprint("eliminar_caso", __name__)
        @simple_page.route("/caso/<int:caso_id>", methods=["DELETE"])
        @cross_origin()
        def f(caso_id):
            caso = Caso.query.get_or_404(caso_id)

            # Eliminar los antecedentes asociados
            if caso.antecedentes:
                db.session.delete(caso.antecedentes)

            # Eliminar el caso
            db.session.delete(caso)
            db.session.commit()

            return jsonify({"message": "Caso eliminado exitosamente"}), 200

        self.llm_bp.append(simple_page)
        print(f"Blueprint created: {simple_page.name} for /caso/<int:caso_id>")

    def getBlueprints(self):
        self.sendResponse()
        self.initDialogue()
        self.getFiles()
        self.getAntecedentesById()
        self.panel()
        self.NuevoCaso()
        self.eliminar_caso()
        self.getCaseInfo()
        print("Blueprints created:", [bp.name for bp in self.llm_bp])  # Print the names of blueprints
        return self.llm_bp
