from ibm_watsonx_ai.foundation_models import Model
from .funcs import get_credentials
import os
import json
class CustomAgent:
    system_prompt = None
    user_prompt = None
    full_prompt = None
    def __init__(self):
        parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 4000,
        "repetition_penalty": 1,
        "temperature" : 1
        }

        self.model = Model(
        model_id = "meta-llama/llama-3-8b-instruct",
        credentials = get_credentials(),
        project_id = '291498a9-1626-4838-81d1-06b5ebb62d3f',
        params=parameters)
    def addSystemPrompt(self,system_prompt):
        self.system_prompt = f"""
        <|start_header_id|>system<|end_header_id|>

        {system_prompt}
        """
    def addUserPrompt(self,user_prompt):
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
        
        The patient should be characterized as follows: {patient_params['descripcion_personaje']}
        
        The patient must answer following all the instructions given by the psychiatrist.

        Por favor, en las respuestas del paciente psiquiatrico no te pases de las 10 palabras

        This is the current conversation:
        """
    
    def parseResponse(response):
        pass

    def getNextResponse(self, doctor_answer):
        if doctor_answer == "/reset":
            self.user_history = f"""
        Please, generate the next patient conversation between the patient and Psychiatrist.

        The following situation occurred to the patient: {self.patient_params['contexto_para_participantes']}
        
        The patient should be characterized as follows: {self.patient_params['descripcion_personaje']}
        
        The patient must answer following all the instructions given by the psychiatrist.

        Por favor, en las respuestas del paciente psiquiatrico no te pases de las 10 palabras

        This is the current conversation:
        """
            return "Se ha eliminado el historial de la conversación"

        self.user_history+=f"""
        
        "speaker": "Doctor",
        "text" : "{doctor_answer}"
        
        """
        
        self.agent.addUserPrompt(self.user_history)
        agent_response = self.agent.runAgent()
        
        self.user_history+=f"""
        {agent_response}"
        """
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