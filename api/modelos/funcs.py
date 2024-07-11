import os
import re
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
#from langchain-ibm import Model
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
# For State Graph
from typing_extensions import TypedDict
import os
# Generation Prompt
from langchain_ibm import WatsonxLLM

llama_3_model = WatsonxLLM(
    model_id="meta-llama/llama-3-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    apikey="0GY8cqsa49R8Gs6aiK0RB5Hb6ZRDFyKew474yYfVJBKa",
    project_id="37e2e673-598a-4dca-af77-b102ee3b47c9",
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




def Nuevo_Caso(antecedentes:str):

    generate_prompt = PromptTemplate(
        template="""

        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>

        You are a friendly AI assistant , which has a task which is to create new cases of people that serve to be interpreted by another AI , the cases are experiences of people who suffered some vulnerability or some problem in their day to day .
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
        Answer:

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>""",
        input_variables=["antecedentes"],
    )

    # Chain
    sql_chain = generate_prompt | llama_3_model | StrOutputParser()


    resultado=sql_chain.invoke({"antecedentes":antecedentes})
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
		"apikey" : "CKncU816nSvrWmBslp8bkyidGa1dceB7imTWr2Kl45VH"
	}