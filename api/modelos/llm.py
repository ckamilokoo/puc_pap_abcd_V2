from ibm_watsonx_ai.foundation_models import Model
from .funcs import get_credentials , analizar_estado
import os
import json
import re
from dotenv import load_dotenv


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
            model_id = "meta-llama/llama-3-1-70b-instruct",
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
        # Aquí actualizamos el prompt con el estado emocional del paciente
        if self.emotional_state:
            emotional_prompt = f"Actualmente el paciente se siente {self.emotional_state}."
            prompt = f"""
            {self.system_prompt}

            {self.user_prompt}

            {emotional_prompt}

            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """
        else:
            prompt = f"""
            {self.system_prompt}
            
            {self.user_prompt}
            
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """

        generated_response = self.model.generate_text(prompt=prompt)
        return generated_response

    def updateEmotionalState(self, state):
        self.emotional_state = state



class Dialogue:
    def __init__(self, agent, patient_params):
        self.agent = agent
        self.patient_params = patient_params
        
        self.user_history = f"""
        Please, generate the next patient conversation between the patient and Psychiatrist.

        The following situation occurred to the patient: {patient_params['contexto_para_participantes']}
        
        The patient should be characterized as follows: {patient_params['descripcion_personaje']}
        
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
        
        # Analizar el estado emocional
        emotion = analizar_estado(agent_response)
        self.agent.updateEmotionalState(emotion)  # Actualizar el estado emocional del agente
        
        print(self.user_history)
        print(agent_response)
        
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

    