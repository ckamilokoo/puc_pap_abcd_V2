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
import asyncio
import datetime

conversation_agent = CustomAgent()
conversation_agent.addSystemPrompt("""
You are an expert in generating a psychiatric patient's response based on what the doctor tells them.

You must respond to the doctor based on the last thing he tells you, try not to repeat the patient's previous responses.

The patient must answer following all the instructions given by the psychiatrist.

You should always generate the response following the following format and in Spanish

"speaker":
"text":


""")
feedback_agent = CustomAgent()
feedback_agent.addSystemPrompt("""
You are a medical specialist in psychiatry, in charge of giving feedback on a conversation.

                                                              
YOU MUST ALWAYS GENERATE THE RESPONSE IN SPANISH

""")

traslator_agent = CustomAgent()
traslator_agent.addSystemPrompt("""
You are an agent specialized on translating from english to spanish
                                
REMEMBER YOU MUST ALWAYS ANSWER IN SPANISH
""")
feedback_agent = CustomAgent()
feedback_agent.addSystemPrompt("""
You are an agentexpert at generating feedback from conversations if the learner is to say whether the doctor was intuitive, able to understand what the patient was saying or whether his or her answers were accurate or not..""")
class LLM_Routes():
    llm_bp = []
    dialogue = None
    init_time = None
    current_time = None
    def endInteraction(self):
        simple_page = Blueprint("endInteraction", __name__)
        @simple_page.route("/endInteraction", methods = ["GET"])
        @cross_origin()
        def f():
            r = self.dialogue.getNextResponse(doctor_answer = "¿Cómo te has sentido teniendo esta conversación conmigo, te ayudó en algo?")
            return jsonify({"response":r}), 200
        self.llm_bp.append(simple_page)
    def getFeedback(self):
        simple_page = Blueprint("getFeedback", __name__)
        @simple_page.route("/getFeedback", methods = ["GET"])
        @cross_origin()
        def f():
            historial = self.dialogue.getUserHistory()
            print(historial)
            feedback_agent.addUserPrompt(f"""
            Give me feedback of the next conversation using the following metrics
                                              A. Active listening: In this state, the person may or may not want to tell their story. Listening to that testimony can be of great help in calming the affected person, so it is essential to give space for them to spontaneously tell what is happening to them, without pressuring them. For other people, keeping quiet will be preferable: staying by their side, in silence, can be very helpful. The central aspect of active listening is being able to transmit to the other person that there is a human being who understands what is happening to them. 
                                              What you should say:In this state, the person may or may not want to tell their story. Listening to that testimony can be of great help in calming the affected person, so it is essential to give space for them to spontaneously tell what is happening to them, without pressuring them. For other people, keeping quiet will be preferable: staying by their side, in silence, can be very helpful. The central aspect of active listening is being able to transmit to the other person that there is a human being who understands what is happening to them.   
                                              What you should not say
                                              -	Do not get distracted
                                              -	Do not look at the clock or look the other way
                                              -	Do not rush to give a solution if the person wants to be heard
                                              -	Do not judge what the person did or did not do, felt or did not feel: 
                                              “You should not have done that”
                                              “You should not feel that way”
                                              Do not tell another person’s story or your own. 
                                              Do not touch the person if you are not sure that it will be well received. 
                                              Do not minimize or give false hope: 
                                              “I can assure you that you will get through this
                                              “Fortunately, it is not that bad”
                                              “Now you have a little angel who takes care of you”
                                              “Don’t worry ... you’re young, and you will find a partner soon”
                                              “God knows why he does things”
                                              “Every cloud has a silver lining”
                                              “Everything happens for a reason”
                                              If the person is very distressed, help them calm down. Offer a glass of water if possible or advance to the next step: Breathing Retraining.
                                              Breathing Techniques:

1.-Approach the person and tell them
“Now we will practice the retraining of breathing: it consists of breathing in, breathing out and then waiting for a moment with our lungs empty before breathing in again... the important thing is to pause after emptying our lungs.”

2.-You can ask them to practice it together.

3.-To begin, ask the person to adopt a relaxed and comfortable posture, putting their feet on the floor and feeling that contact.
“If you want and feel comfortable, you can close your eyes or look at a fixed point with your eyes down. Now let’s try ...”
 
1.	BREATHING IN: Counting to 4
2.	BREATHING OUT THROUGH THE NOSE OR MOUTH: Counting to 4
3.	RETENTION WITH “EMPTY” LUNGS: Counting to 4
 
 Counting to 4 does not necessarily mean 4 seconds. The duration of the times is variable, depending on the state of agitation of the person. Accommodate the length of time so that the affected person feels comfortable and does not run out of air

 “To help yourself, you can mentally and slowly repeat the word calm each time you breathe out or you can imagine that the tension escapes with the air you breathe out. Let’s try again ...”  

Once the affected person has understood the mechanics, you can let them continue for only 10 minutes, reinforcing how well they are doing:

“very good… you’re doing great.”

In addition, you can also use the adapted guidelines of Foa, Hembree and Rothbaum (2007) for the breathing retraining, which follow the same logic previously explained
 
· Explain in detail the logic of the exercise: 
“The way we breathe modifies our emotions. When we breath out we relax more than when we breath in (contrary to what is usually believed), so we can enter a calm state if we extend the time our lungs are empty ...”

· Explain and demonstrate the mechanics of the exercise: 
“In this exercise you need to breath counting to four, breath out counting to four and wait counting to four before inhaling again.” Now look at how I do it... [do it yourself].

· Join them in doing the exercise: 
“Now you do the exercise and I will accompany you by reminding you how you should do it. Inhale... two, three, four ... exhale, two, three four ... hold, two three, four ... "[repeat the cycle for one or two minutes accompanying the affected person]. “While exhaling, you can think of the word calm."

· Tell the affected person to do it daily for ten minutes, three times a day (morning, evening, night), and every time they feel distressed. You can use the Breath Pacer or Paced Breathing apps available for smart phones: 

“I am going to ask you to do this exercise for 10 minutes every day in the morning when you wake up, after lunch, before going to sleep and every time you feel that you are beginning to feel anxious. The more you use this technique, the easier it will be the next time you use it." You can use some free applications available for cellphones, such as Breath Pacer and Paced Breathing.

C. Classification of Needs
After a traumatic event it is common for mental confusion to occur and people have difficulty organizing the different steps they must follow to solve their problems (e.g. incident claims, calling relatives, searching for belongings, legal procedures, etc.) You can help the person a lot by accompanying them in the process of prioritizing their needs, and then helping them contact the health and social security services that may be of help. Remember that this is a brief intervention, and your work focuses on helping identify needs and prioritize them. It is important that the person uses their own resources or those of their personal or community support networks to cope with the crisis they are experiencing, so that what is achieved is maintained after you finish your work.
What you should do or say 
Listen to the story and identify the concerns of the affected person 
“What is your concern or need now? Can I help you solve it? “

Help people prioritize their needs: You can ask them to distinguish between what they need to solve immediately and what can wait: 

“... I realize that there are many things that concern you. How about we go step by step and focus first on what’s most urgent?

What you should NOT do or say 
Decide what their needs are, without paying attention to the affected person’s story. 
“Before you tell me anything, I think the most important thing you should do is...”

Resolve the needs as the affected person mentions them, without organizing or prioritizing. 

You can also try with the following sentences (available in Figueroa, Cortés, Accatino and Sorensen, 2016): 
• “What do you think is the most important problem to solve first?” 
• “What things have helped you in the past when you have had to deal with this much stress?” 
• “Obviously there are too many problems together, so it would be a good idea to order them and go one by one ... if you want I can help you do it.” 
• “I understand that you feel overwhelmed. Let’s see if we can identify at least three things that you currently have control over to focus on.” 

D. Direct to Support Networks
Once these needs have been identified, help the person contact the people and/or social support services that can help them meet these needs now and later, next to the material Services and Support Networks (see Annex). 
Always remember that the first support network is family and friends. For this step, it is essential that before contacting the affected person, you study the offer of social support services available in the place where PFA will be provided.
What you should do or say
Facilitate contact with the person’s family, friends and/or work. Suggest calling them if necessary (identify available public telephones or manage a cell phone with your institution).
Make practical suggestions on how to receive the help needed. 
Use the contact information available in the Services and Support Networks material.
What you should NOT do or say
Take the initiative to “help” the person with issues that themselves can do.
“I will go talk to the social worker about your mother’s situation”
“Give me your cell phone, I’ll call your son to tell him what happened”
You can take advantage of the following useful phrases (available in Figueroa, Cortés, Accatino and Sorensen, 2016): 
• “Does your family know what happened and that you are here?” 
• “It is very helpful to be with friends and family ... spend time together, be accompanied; is there a time in the week you can regularly spend time with your friends and family?” 
• “I understand that you may distrust public support services, but if you later change your mind, I would like you to know how to contact them.” 
• “I do not have information about the situation of your children, but let’s see if we can find out something about them in sites that search for people or with the police ...” 
• “If you have any doubts later, you can come and ask me, or maybe you will want to call the toll-free number Salud Responde (600 360 7777), where someone can guide you 24/7” 
E. Psycho-education
Finally, promote positive response strategies to stressful situations, explaining and delivering a copy of the material, What can I Expect in a Crisis? (See Annex). Review the material with the affected person and answer their questions. 
You can use the following table, which is useful to know the normal reactions in stressful situations or recent traumatic experiences. 
It is very important that you normalize those emotional reactions that, although somewhat uncomfortable, are normal in crisis situations, such as emotional lability, difficulty thinking, insomnia, anxiety, among others. In this way the person will not interpret what happens to them as a sign of “losing their mind”. Emphasize that it is most likely that the discomfort they feel will go away in a few weeks without help, show them how to help themselves and their acquaintances, what the warning signs are, and what to do if they appear.
                                              
            {historial}
            
            """)
            response= feedback_agent.runAgent()
            traslator_agent.addSystemPrompt(f"""
            please, translate the following text from english to spanish
                                            
            {response}

            remember answer in spanish
            """)
            translated_response = traslator_agent.runAgent()
            return jsonify({"response": f"{translated_response}"}),200
        self.llm_bp.append(simple_page)
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
            self.current_time = datetime.datetime.now()
            print(self.current_time - self.init_time)
            dif = self.current_time - self.init_time
            if (dif > datetime.timedelta(minutes=20)):
                return jsonify({"response": {
        "speaker": "",
        "text": "El tiempo ha finalizado"
    }})
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
            self.init_time = datetime.datetime.now()
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
            print(casos)
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
        
    def chatbot(self):
        simple_page=Blueprint("chatbot", __name__)
        @simple_page.route("/chat", methods=["GET"])
        @cross_origin()
        def f():
            
            return render_template("chatbot.html")
        self.llm_bp.append(simple_page)
        print(f"Blueprint created: {simple_page.name} for /chat")
        
    
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
        self.getFeedback()
        self.endInteraction()
        self.chatbot()
        print("Blueprints created:", [bp.name for bp in self.llm_bp])  # Print the names of blueprints
        return self.llm_bp
