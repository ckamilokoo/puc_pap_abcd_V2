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

    def __init__(self):
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 4000,
            "repetition_penalty": 1,
            "temperature" : 1
        }

        self.model = Model(
            model_id = "meta-llama/llama-3-70b-instruct",
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
    def __init__(self, agent, patient_params):
        self.agent = agent
        self.patient_params = patient_params
        
        self.user_history = f"""
        Please, generate the next patient conversation between the patient and Psychiatrist.

        The following situation occurred to the patient: {patient_params['contexto_para_participantes']}
        
        The patient should be characterized as follows: {patient_params['descripcion_personaje']}  , which you must remember to give your patient's answers.
        
        The patient must answer following all the instructions given by the psychiatrist , You should always say hello first when you are greeted.
        you should never mention your problem in the patient's context right away, you should always wait for the doctor to ask you how you feel or what is the problem that is bothering you or that you are suffering from.

        Por favor, en las respuestas del paciente psiquiatrico no te pases de las 10 palabras

        This is the current conversation:
        """
        self.initial_len = len(self.user_history)

    def getNextResponse(self, doctor_answer):
        if doctor_answer == "/reset":
            self.user_history = f"""
            Please, generate the next patient conversation between the patient and Psychiatrist.

            The following situation occurred to the patient: {self.patient_params['contexto_para_participantes']}
            
            The patient should be characterized as follows: {self.patient_params['descripcion_personaje']}
            
            The patient must answer following all the instructions given by the psychiatrist , You should always say hello first when you are greeted.
            you should never mention your problem in the patient's context right away, you should always wait for the doctor to ask you how you feel or what is the problem that is bothering you or that you are suffering from.

            Por favor, en las respuestas del paciente psiquiatrico no te pases de las 10 palabras

            This is the current conversation:
            """
            return "Se ha eliminado el historial de la conversación"

        # Agregar la respuesta del doctor
        self.user_history += f"""
        "speaker": "Doctor",
        "text": "{doctor_answer}"
        """
        
        # Generar respuesta del modelo
        self.agent.addUserPrompt(self.user_history)
        agent_response = self.agent.runAgent()
        
        # Actualizar el historial con la respuesta del agente
        self.user_history += f"""
        {agent_response}
        """
        print(agent_response)
        print(self.user_history)
        
        
        agent_response = "{"+agent_response+"}"
        return json.loads(agent_response)

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

            
    # Función para enviar la información del caso a la API
    def send_case_to_api(self,contexto, descripcion,escala):
        api_url = "http://127.0.0.1:8000/casos/"
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
        api_url = f"http://127.0.0.1:8000/casos/"
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
        api_url = "http://127.0.0.1:8000/casos/"
        try:
            response = requests.delete(api_url)
            if response.status_code == 200:
                return response.json()  # Mensaje de éxito
            else:
                return {"status": "error", "message": "Error al eliminar casos", "details": response.text}
        except Exception as e:
            return {"status": "error", "message": "Excepción al eliminar casos", "details": str(e)}

    