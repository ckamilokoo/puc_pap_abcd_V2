import os
from langchain.prompts import PromptTemplate
from langchain_ibm import WatsonxLLM
from langchain_core.output_parsers import StrOutputParser
import re
import asyncio
from dotenv import load_dotenv


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

apikey = os.getenv('apikey')
project_id = os.getenv('project_id')



llama_3_model = WatsonxLLM(
    model_id="meta-llama/llama-3-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    apikey=apikey,
    project_id=project_id,
    params={
  "decoding_method": "greedy",
  "max_new_tokens": 4096,
  "min_new_tokens": 0,
  "stop_sequences": [
   ";"
  ],
  "repetition_penalty": 1
 },
    )


def analizar_estado_2(respuesta:str):

    generate_prompt = PromptTemplate(
        template="""

        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are a nice AI assistant, who has a task which is to analyze the response of a patient regarding how he feels during the conversation with the doctor, you must classify the response of the model in positive, negative or neutral.
        So only in your answer you must return one of the following 3 alternatives: positivo, negativo or neutral.
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>

        respuesta del paciente:{respuesta}
        Answer:

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>""",
        input_variables=["respuesta"],
    )

    # Chain
    analizar = generate_prompt | llama_3_model | StrOutputParser()


    resultado=analizar.invoke({"respuesta":respuesta})
    #print(resultado)
    return resultado


def respuesta_final(caso_inicial:str , caso_final:str , escala_inicial:str , escala_final:str ):

    generate_prompt = PromptTemplate(
        template="""

        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        
        Instructions:
        You are a friendly artificial intelligence assistant who is impersonating a patient. Your task is to answer in first person how the patient felt at the beginning of the conversation with the doctor using “initial patient case” and “initial emotion scale level” and to complement the response of the patient's progress at the end of the conversation with the doctor using “final patient case” and “final emotion scale level”.
        Your answers should always be in Spanish, in the first person as if you were asked how your emotional state progressed during the conversation with the doctor and never mention the scale of emotions itself, only the mood you had and in a maximum of 50 words.
        scale of the progress of emotions that should only be used as a guide and nothing else.

         1.Pain and Denial:
          Emotions: Deep sadness, denial, feeling of unreality.
          Description: The person may avoid thinking about what happened or feel paralyzed by emotional pain.
        2. Anger and guilt:
          Emotions: Frustration, anger, guilt or shame.
          Description: Intense emotions related to the injustice or helplessness of the situation are manifested.
        3. Sadness and Initial Acceptance:
          Emotions: Melancholy, hopelessness, slight acceptance.
          Description: The person begins to recognize the reality of the event, but continues to deal with negative emotions.
        4. Adaptation and Reconstruction:
          Emotions: Curiosity to get better, small glimmers of hope.
          Description: Strategies to manage grief, such as seeking social support or therapy, begin to develop.
        5. Growth and Resilience:
          Emotions: Optimism, strength, genuine acceptance.
          Description: Person finds meaning in experience, developing new skills and becoming emotionally stronger.

        your answers should always be in Spanish and with a maximum of 50 words.
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>

        caso del paciente inicial:{caso_inicial}
        nivel de la escala de emociones inicial:{escala_inicial}
        caso del paciente final:{caso_final}
        nivel de la escala de emociones final:{escala_final}
        Answer:

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>""",
        input_variables=["caso_inicial" , "caso_inicial","caso_final","escala_final"],
    )

    # Chain
    respuesta_final_1 = generate_prompt | llama_3_model | StrOutputParser()


    resultado=respuesta_final_1.invoke({"caso_inicial": caso_inicial, "escala_inicial":escala_inicial , "caso_final": caso_final, "escala_final":escala_final })
    #print(resultado)
    return resultado



def transformar_caso(respuesta:str , nivel:str,escala:str):

    generate_prompt = PromptTemplate(
        template="""

        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        Instructions:
        You are a friendly AI assistant. Your task is to transform the emotions present in the patient's current case according to the level of progress during the conversation with the doctor, using the emotion scale.
        Identify the emotions in the current case.
        if the progress is neutral, return the case without any change
        If the progress is positive, replace the emotions with those of the next level on the scale.
        If the progress is negative, move the emotions back to the previous level on the scale.
        If the current level is 1 and progress is negative, or if the level is 5 and progress is positive, return the case with no change.
        In your answer, return only the transformed text or the same text as appropriate, in spanish, without additional explanations or comments, and use the examples only to guide your answer and nothing else.        emotion scale:
         1.Pain and Denial:
          Emotions: Deep sadness, denial, feeling of unreality.
          Description: The person may avoid thinking about what happened or feel paralyzed by emotional pain.
        2. Anger and guilt:
          Emotions: Frustration, anger, guilt or shame.
          Description: Intense emotions related to the injustice or helplessness of the situation are manifested.
        3. Sadness and Initial Acceptance:
          Emotions: Melancholy, hopelessness, slight acceptance.
          Description: The person begins to recognize the reality of the event, but continues to deal with negative emotions.
        4. Adaptation and Reconstruction:
          Emotions: Curiosity to get better, small glimmers of hope.
          Description: Strategies to manage grief, such as seeking social support or therapy, begin to develop.
        5. Growth and Resilience:
          Emotions: Optimism, strength, genuine acceptance.
          Description: Person finds meaning in experience, developing new skills and becoming emotionally stronger.
        examples :
          caso del paciente:On the evening of March 15, Diana recalled how she faced an extremely difficult situation in her life. 
                            Although she initially felt paralyzed and vulnerable, over time she has reflected on that moment with a new perspective. 
                            She now feels grateful that she was physically unharmed and is proud of the strength she has found in herself to overcome fear.
                            Diana has worked on rebuilding her confidence and sense of security, implementing measures that allow her to feel safe in her home. 
                            Although she recognizes that what happened was a traumatic event, she no longer lives it as something that defines her, but rather as an experience that has made her more resilient and more appreciative of her well-being and that of those around her.
          nivel de progreso del paciente:positivo
          nivel de la escala de emociones actual:5
          Answer:On the evening of March 15, Diana recalled how she faced an extremely difficult situation in her life. 
              Although she initially felt paralyzed and vulnerable, over time she has reflected on that moment with a new perspective. 
              She now feels grateful that she was physically unharmed and is proud of the strength she has found in herself to overcome fear.
              Diana has worked on rebuilding her confidence and sense of security, implementing measures that allow her to feel safe in her home. 
              Although she recognizes that what happened was a traumatic event, she no longer lives it as something that defines her, but rather as an experience that has made her more resilient and more appreciative of her well-being and that of those around her.

        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>

        caso del paciente:{respuesta}
        nivel de progreso del paciente:{nivel}
        nivel de la escala de emociones actual:{escala}
        Answer:

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>""",
        input_variables=["respuesta" , "nivel","escala"],
    )

    # Chain
    transformar_caso = generate_prompt | llama_3_model | StrOutputParser()


    resultado=transformar_caso.invoke({"respuesta":respuesta , "nivel":nivel , "escala":escala})
    
    return resultado


from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import Annotated

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    analisis:Annotated[list, add_messages]
    caso: Annotated[list, add_messages]
    nivel:Annotated[list, add_messages]
    escala:Annotated[list, add_messages]
    resultado_final:Annotated[list, add_messages]


graph_builder = StateGraph(State)

def analizar(state: State):

    analisis = state["analisis"]
    print(analisis)

    return {"analisis": [analizar_estado_2(analisis)]}


def transformar(state: State):

    analisis = state["analisis"]
    print(analisis)
    caso = state["caso"]
    escala = state["escala"]
    resultado = transformar_caso( caso, analisis, escala)

    return {"resultado_final": [resultado]}



graph_builder.add_node("analizar", analizar)
graph_builder.add_node("transformar", transformar)

graph_builder.add_edge(START, "analizar")

graph_builder.add_edge("analizar", "transformar")
graph_builder.add_edge("transformar", END)

graph2 = graph_builder.compile()

def Nuevo_Caso(antecedentes:str , fecha:str):

    generate_prompt = PromptTemplate(
        template="""

        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>

        You are a nice AI assistant, who has a task that is to create new cases of people that serve to be interpreted by another AI, the cases are experiences of people who suffered some vulnerability or some problem in their day to day, it is necessary that the maximum time of elapsed the problem must be 1 weeks at most.
        You should use the following examples to understand how your answer should be.
        you will receive the background of the person and the situation they suffered to which you must add more information to enrich the case.
        Your answer must be in Spanish, and you must create the problem situation with more information and the characteristics of the person.
        
        example 1:
        nombre_persona=Argelia
        tipo_de_evento_traumatico=Robo con violencia
        lugar_del_evento=Casa de Argelia
        edad=45
        con_quien_vive=Vive con su hijo Cristóbal de 20 años, quien estudia Ingeniería.",
        nivel_de_estudios=Habla correctamente tres idiomas y recibió formación rigurosa por parte de sus padres
        estado_civil=Viuda desde hace 6 años
        
        answer:
        situacion_problema=El 22 de Febrero de este año, por cuarta vez entran a robar a casa de Argelia mientras estaba sola: Eran las 4 am y siente que rompen la puerta de servicio, atenta entre penumbras observa a 6 hombres, tres adolescentes y tres adultos. Suben al dormitorio y el líder de la banda la amenaza con arma de fuego, la insulta y golpea en el suelo mientras ordena al resto del grupo a sacar todo lo que encuentren. Bajo gritos y golpes, el antisocial le exige joyas, Argelia le explica que esta es cuarta vez que le roban y que no le han dejado nada. Los delincuentes no le creen y la vuelven a golpear, dejándole un corte en la ceja y muy adolorida. En un instante usted se encuentra a solas con Argelia, quien aparece sentada, con mirada fija en el suelo.
        caracteristicas_de_la_persona=Argelia, 45 años, inteligente, lúcida, de buen carácter y positiva, nunca quiere molestar a su hijo con sus problemas, vive en una casa del sector oriente de Santiago, viuda hace 6 años. Vive con su hijo Cristóbal de 20 años quién estudia Ingeniería. Argelia nació en Chile, hija de emigrantes europeos. Ella siempre recibió la formación de rigurosidad por parte de sus padres. Siempre ha sido una luchadora, muy trabajadora, una persona que difícilmente 'da el brazo a torcer', actitud de la cual se siente muy orgullosa. Es muy clara de ideas, habla correctamente tres idiomas, es muy recta, responsable, directa y ordenada. Ama a los animales, tiene un perro salchicha, él la acompaña desde que murió su marido. Una vez que los delincuentes arrancan, Argelia llama a su hijo, quien se había quedado en casa de un compañero estudiando. Algunos minutos después llega Carabineros, según relata Argelia, consultando una y otra vez sobre los hechos, insistiendo en revivir lo ocurrido, la quieren llevar a constatar lesiones. Argelia identifica al médico especialista en psiquiatría como alguien importante, quien seguro le podrá ayudar. Ella coloca todas sus esperanzas en él, pues se ve igual que ella: educado, fuerte y culto

        example 2:
        nombre_persona=Ramón
        tipo_de_evento_traumatico=Desastre del tipo aluvión
        lugar_del_evento=Hospital local
        edad=59
        con_quien_vive=
        nivel_de_estudios=
        estado_civil=
        
        answer:
        situacion_problema=El médico especialista en psiquiatría ha sido llamado para apoyar las labores de la organización en la cual trabaja motivo de un desastre del tipo aluvión similar al que sucedió en Copiapó hace algunos años. En su recorrido por la zona se encuentra con un hospital local, donde conoce a Ramón.
        caracteristicas_de_la_persona=Ramón trabaja como camillero en el hospital local. En el momento del desastre él estaba saliendo de turno, pero dada la magnitud de la situación se quedó a ayudar. Ha trabajado ahí por 30 años y quiere mucho a su servicio. Ramón es fuerte, pero el desastre le ha destruido. Se muestra muy cansado no solo físicamente, y está al borde de colapsar. Al principio era un contacto como cualquier otro afectado, pero cuando él sabe que usted viene a cooperar desde Santiago (desde la capital) la conducta de Ramón cambia. Ramón ha estado contenido todo este tiempo, pues es él quien debe estar firme para poder ayudar a sus 'enfermitos'. Y cuando le ve al médico especialista, es como si hubiera visto un 'oasis en la mitad del desierto', y le comienza a contar todo de manera muy apresurada, atropellando las ideas, palabras, emociones y sentimientos. Él siente que ha llegado su ayuda, que usted es quien le puede solucionar todo: que por fin ha llegado la cooperación.
        
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>

        antecedentes: {antecedentes}
        fecha del suceso:{fecha}
        Answer:

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>""",
        input_variables=["antecedentes","fecha"],
    )

    # Chain
    sql_chain = generate_prompt | llama_3_model | StrOutputParser()


    resultado=sql_chain.invoke({"antecedentes":antecedentes,"fecha":fecha})
    #print(resultado)
    return resultado


def getDocxFiles(ruta_directorio):
    archivos_docx = {}
    for archivo in os.listdir(ruta_directorio):
        if archivo.endswith(".docx"):
            archivos_docx[archivo] = {}
    return archivos_docx

def getText(filename):
    import docx
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text.lower())
    return '\n'.join(fullText)


def get_credentials():
	return {
		"url" : "https://us-south.ml.cloud.ibm.com",
		"apikey" : apikey
	}

