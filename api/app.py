from flask import Flask
from flask_smorest import Api
from rutas.llm_routes import LLM_Routes
from config import ServerConfig
from casos.models import db, Caso , Antecedentes


app = Flask(__name__)
app.config.from_object(ServerConfig)



db.init_app(app)

# Configuración Swagger
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Paciente Virtual"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

# Inicializar rutas
router = LLM_Routes()
for blueprint in router.getBlueprints():
    api.register_blueprint(blueprint)

with app.app_context():
    # Crear las tablas en la base de datos si no existen
    db.create_all()
    
    # Verificar si hay casos predefinidos en la base de datos
    if not Caso.query.first():
        # Insertar casos predefinidos solo si la base de datos está vacía
        # Insertar Caso Argelia
        caso1 = Caso(
            nombre="Argelia",
            situacion_problema="El 22 de Febrero de este año, por cuarta vez entran a robar a casa de Argelia mientras estaba sola: Eran las 4 am y siente que rompen la puerta de servicio, atenta entre penumbras observa a 6 hombres, tres adolescentes y tres adultos. Suben al dormitorio y el líder de la banda la amenaza con arma de fuego, la insulta y golpea en el suelo mientras ordena al resto del grupo a sacar todo lo que encuentren. Bajo gritos y golpes, el antisocial le exige joyas, Argelia le explica que esta es cuarta vez que le roban y que no le han dejado nada. Los delincuentes no le creen y la vuelven a golpear, dejándole un corte en la ceja y muy adolorida. En un instante usted se encuentra a solas con Argelia, quien aparece sentada, con mirada fija en el suelo.",
            caracteristicas_de_la_persona="Argelia, 45 años, inteligente, lúcida, de buen carácter y positiva, nunca quiere molestar a su hijo con sus problemas, vive en una casa del sector oriente de Santiago, viuda hace 6 años. Vive con su hijo Cristóbal de 20 años quién estudia Ingeniería. Argelia nació en Chile, hija de emigrantes europeos. Ella siempre recibió la formación de rigurosidad por parte de sus padres. Siempre ha sido una luchadora, muy trabajadora, una persona que difícilmente 'da el brazo a torcer', actitud de la cual se siente muy orgullosa. Es muy clara de ideas, habla correctamente tres idiomas, es muy recta, responsable, directa y ordenada. Ama a los animales, tiene un perro salchicha, él la acompaña desde que murió su marido. Una vez que los delincuentes arrancan, Argelia llama a su hijo, quien se había quedado en casa de un compañero estudiando. Algunos minutos después llega Carabineros, según relata Argelia, consultando una y otra vez sobre los hechos, insistiendo en revivir lo ocurrido, la quieren llevar a constatar lesiones. Argelia identifica al médico especialista en psiquiatría como alguien importante, quien seguro le podrá ayudar. Ella coloca todas sus esperanzas en él, pues se ve igual que ella: educado, fuerte y culto."
        )

        antecedentes1 = Antecedentes(
            nombre_persona="Argelia",
            tipo_de_evento_traumatico="Robo con violencia",
            lugar_del_evento="Casa de Argelia",
            edad=45,
            con_quien_vive="Vive con su hijo Cristóbal de 20 años, quien estudia Ingeniería.",
            nivel_de_estudios="Habla correctamente tres idiomas y recibió formación rigurosa por parte de sus padres.",
            estado_civil="Viuda desde hace 6 años."
        )

        caso1.antecedentes = antecedentes1
        db.session.add(caso1)

        # Insertar Caso Ramón
        caso2 = Caso(
            nombre="Ramón",
            situacion_problema="El médico especialista en psiquiatría ha sido llamado para apoyar las labores de la organización en la cual trabaja motivo de un desastre del tipo aluvión similar al que sucedió en Copiapó hace algunos años. En su recorrido por la zona se encuentra con un hospital local, donde conoce a Ramón.",
            caracteristicas_de_la_persona="Ramón trabaja como camillero en el hospital local. En el momento del desastre él estaba saliendo de turno, pero dada la magnitud de la situación se quedó a ayudar. Ha trabajado ahí por 30 años y quiere mucho a su servicio. Ramón es fuerte, pero el desastre le ha destruido. Se muestra muy cansado no solo físicamente, y está al borde de colapsar. Al principio era un contacto como cualquier otro afectado, pero cuando él sabe que usted viene a cooperar desde Santiago (desde la capital) la conducta de Ramón cambia. Ramón ha estado contenido todo este tiempo, pues es él quien debe estar firme para poder ayudar a sus 'enfermitos'. Y cuando le ve al médico especialista, es como si hubiera visto un 'oasis en la mitad del desierto', y le comienza a contar todo de manera muy apresurada, atropellando las ideas, palabras, emociones y sentimientos. Él siente que ha llegado su ayuda, que usted es quien le puede solucionar todo: que por fin ha llegado la cooperación.",
            
            
        )

        antecedentes2 = Antecedentes(
            nombre_persona="Ramón",
            tipo_de_evento_traumatico="Desastre del tipo aluvión",
            lugar_del_evento="Hospital local",
            edad=59,
            con_quien_vive="",
            nivel_de_estudios="",
            estado_civil=""
        )

        caso2.antecedentes = antecedentes2
        db.session.add(caso2)

        # Hacer commit para guardar los cambios en la base de datos
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=False,port=8080)


