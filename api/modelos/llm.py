from ibm_watsonx_ai.foundation_models import Model
from .funcs import get_credentials 
import os
import json
import re
from dotenv import load_dotenv
import requests


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

apikey = os.getenv('apikey')
project_id = os.getenv('project_id')

class CustomAgent:
    system_prompt = None
    user_prompt = None
    full_prompt = None
    emotional_state = None  # Almacenar estado emocional

    def __init__(self,custom_model = "meta-llama/llama-3-405b-instruct"):
        self.custom_model = custom_model
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 4000,
            "repetition_penalty": 1,
            "temperature" : 1
        }

        self.model = Model(
            model_id = custom_model,
            credentials = get_credentials(),
            project_id = project_id,
            params=parameters
        )

    def addSystemPrompt(self, system_prompt):
        self.system_prompt = f"""
        <|start_header_id|>system<|end_header_id|>

        {system_prompt}
        """

    def addUserPrompt(self, user_prompt):
        self.user_prompt = f"""
        <|begin_of_text|><|eot_id|><|start_header_id|>user<|end_header_id|>
        {user_prompt}
        """

    def runAgent(self):
        prompt = f"""
            {self.system_prompt}
            
            {self.user_prompt}
            
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """

        generated_response = self.model.generate_text(prompt=prompt)
        return generated_response

class Dialogue:
    def __init__(self, agent, agent_techniques,patient_params):
        self.agent = agent
        self.patient_params = patient_params
        self.agent_techniques = agent_techniques
        self.last_techniques_applied = ""
        self.user_history = f"""
        Task: Please generate the next segment of a patient-psychiatrist conversation.
        
        Context: The following situation occurred to the patient:
        

        {self.patient_params['contexto_para_participantes']}
        Techniques Applied by the Specialist:

        
        Patient Characterization:
        The patient is an ordinary person with natural emotions like anyone else.
        The patient can appear hostile toward the doctor if they feel offended or threatened.
        The patient can be grateful if the doctor helps them.
        The patient should be characterized as follows:
        {self.patient_params['descripcion_personaje']}
        
        Instructions for the Patient’s Responses:
        
        Most importantly, the patient must demonstrate behavioral improvement based on the techniques that the specialist applied on him/her.
        The patient must appear natural in their responses.
        The patient must follow all instructions given by the psychiatrist.
        The patient should always say “hello” first when greeted by the psychiatrist.
        The patient should never mention their problem or context immediately. The patient should wait for the psychiatrist to specifically ask how they feel, what is bothering them, or what they are suffering from.
        The patient should not exceed 30 words in their responses.
        The patient should gradually show improved behavior (as noted above) based on the specialist’s applied techniques.
        Current Conversation:
                    """
        
        self.initial_len = len(self.user_history)

    def getNextResponse(self, doctor_answer):
        if doctor_answer == "/reset":
            self.user_history = f"""
         Task: Please generate the next segment of a patient-psychiatrist conversation.
        
        Context: The following situation occurred to the patient:
        

        {self.patient_params['contexto_para_participantes']}
        Techniques Applied by the Specialist:

        
        Patient Characterization:
        The patient is an ordinary person with natural emotions like anyone else.
        The patient can appear hostile toward the doctor if they feel offended or threatened.
        The patient can be grateful if the doctor helps them.
        The patient should be characterized as follows:
        {self.patient_params['descripcion_personaje']}
        
        Instructions for the Patient’s Responses:
        Most importantly, the patient must demonstrate behavioral improvement based on the techniques that the specialist applied on him/her.
        The patient must appear natural in their responses.
        The patient must follow all instructions given by the psychiatrist.
        The patient should always say “hello” first when greeted by the psychiatrist.
        The patient should never mention their problem or context immediately. The patient should wait for the psychiatrist to specifically ask how they feel, what is bothering them, or what they are suffering from.
        The patient should not exceed 30 words in their responses.
        The patient should gradually show improved behavior (as noted above) based on the specialist’s applied techniques.
        Current Conversation:
                    
            
            """
            self.last_techniques_applied = ""
            return "Se ha eliminado el historial de la conversación"

        # Agregar la respuesta del doctor
        self.user_history += f"""
        "speaker": "Specialist",
        "text": "{doctor_answer}"
        """
        
        # Generar respuesta del modelo
        self.agent.addUserPrompt(self.user_history)
        agent_response = self.agent.runAgent()

        # Vemos las técnicas utilizadas

        
        
        # Actualizar el historial con la respuesta del agente
        self.user_history += f"""
        {agent_response}
        """

        #print(agent_response)
        #print(self.user_history)
        
        self.addTechniquesToHistorial()
        agent_response = "{"+agent_response+"}"
        return json.loads(agent_response)
    def addTechniquesToHistorial(self):
        prompt_techniques = f"""This is the current conversation, please identify the techniques used by the specialist:
        {self.user_history}"""
        self.agent_techniques.addUserPrompt(prompt_techniques)
        response = self.agent_techniques.runAgent()
        pattern = "Techniques Applied by the Specialist:"
        idx = self.user_history.find(pattern)
        first_cut = self.user_history[0:idx+len(pattern)]
        first_cut+=f"\n{response}\n"
        first_cut+=self.user_history[idx+len(pattern):]
        self.user_history = first_cut
        self.user_history.replace(self.last_techniques_applied, "")
        self.last_techniques_applied = response
        #print(self.user_history)

    def getUserHistory(self):
        return self.user_history

    def initDialogue(self, n_interactions):
        idx = 0
        while n_interactions > idx:
            next_question = input("")
            response = self.getNextResponse(next_question)
            print(response)
            idx += 1
            
    def addHistory(self, historial_recortado):
        """Añade un historial recortado al historial del usuario."""
        self.user_history += f"\n{historial_recortado}"
        print("Historial actualizado:", self.user_history)
        return self.user_history

            
    # Función para enviar la información del caso a la API
    def send_case_to_api(self,contexto, descripcion,escala):
        api_url = os.getenv("Segundo_Backend")
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "contexto": contexto,
            "descripcion": descripcion,
            "escala":escala,
        }

        try:
            response = requests.post(api_url, json=body, headers=headers)
            if response.status_code == 200:
                return {"status": "success", "message": "Caso enviado con éxito"}
            else:
                return {"status": "error", "message": "Error al enviar el caso", "details": response.text}
        except Exception as e:
            return {"status": "error", "message": "Excepción al enviar el caso", "details": str(e)}
        
        
    # Nueva función para obtener información del backend
    def get_casos_from_backend(self):
        api_url = os.getenv("Segundo_Backend")
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                return response.json()  # Retornar los casos como un JSON
            else:
                return {"status": "error", "message": "Error al obtener casos", "details": response.text}
        except Exception as e:
            return {"status": "error", "message": "Excepción al obtener casos", "details": str(e)}

    # Nueva función para eliminar toda la información de la base de datos
    def delete_all_casos_from_backend(self):
        api_url = os.getenv("Segundo_Backend")
        try:
            response = requests.delete(api_url)
            if response.status_code == 200:
                return response.json()  # Mensaje de éxito
            else:
                return {"status": "error", "message": "Error al eliminar casos", "details": response.text}
        except Exception as e:
            return {"status": "error", "message": "Excepción al eliminar casos", "details": str(e)}

    