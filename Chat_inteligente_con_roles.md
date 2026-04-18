# Chat inteligente con roles

## Descripción

Es una aplicación de chat donde el usuario selecciona un rol antes de hacer una pregunta (por ejemplo: profesor, programador, psicólogo o experto en negocios). Según el rol elegido, el sistema modifica el prompt que se envía al modelo en Ollama para que la respuesta tenga ese estilo y enfoque.

Por ejemplo, si se elige “profesor”, la respuesta será más explicativa; si se elige “programador”, será más técnica.

Permite demostrar el uso de IA generativa y conceptos básicos de comportamiento “agentico”.

### PROPUESTA DE SOLUCIÓN

Toda la propuesta que se da a continuación es una idea general tomando en cuenta un presupuesto 0.

- 1-Conectar un AI (ollama - llms locales)
  -1.1a travez puede API REST conectarlo hacia -->
  --WhatsApp (<https://bot-whatsapp.netlify.app/>),
  --Telegram (<https://github.com/python-telegram-bot/python-telegram-bot>)
  --ROL DEL AGENTE: (profesor, programador, psicólogo o experto en negocios)

---

Principios SDD:
El Desarrollo Guiado por Especificaciones (SDD, por sus siglas en inglés) es una metodología moderna de ingeniería de software donde la documentación detallada y los requisitos técnicos (especificaciones) son la "fuente de verdad" central, utilizada para instruir a la IA a generar código. A diferencia de TDD (pruebas primero), el SDD se enfoca en definir exhaustivamente el "qué" antes de programar, permitiendo que la IA produzca tests y funcionalidad alineados con la intención del desarrollador

---

¿Qué es el desarrollo guiado por pruebas? TDD vs. BDD vs. SDD

<https://testrigor.com/blog/what-is-test-driven-development-tdd-vs-bdd-vs-sdd/#section-what_is_tdd>

TDD es una práctica de desarrollo de software basada en pruebas, que combina la codificación y la escritura iterativas de pruebas unitarias. TDD se centra en desarrollar funcionalidades más pequeñas de forma aislada.

TDD y BDD pueden parecer muy similares, ya que ambas estrategias incluyen escribir pruebas antes de escribir el código para garantizar una aplicación sin errores. Sin embargo, BDD prueba el comportamiento de una aplicación desde la perspectiva del usuario final. BDD se centra más en el resultado del escenario general que en un método específico.

El TDD puede ser realizado por un solo desarrollador, mientras que, en el BDD, varias partes interesadas, que pueden incluir gerentes de producto, evaluadores y desarrolladores, colaboran antes de idear un escenario de prueba.

<https://github.com/j0k3r-dev-rgl/sdd-engram-plugin>

STACK =

--WORKFLOW

--Contexto (empresarial: Modelo de negocio de la empresa.)
--- Misión, visión, valores.
--- Productos o servicios.
--- Políticas de la empresa.
--- Horarios de atención.
--- Preguntas frecuentes (FAQs).

--Contexto (Educativo: Temas de interés del usuario.)
--- Materias o áreas de estudio.
--- Dificultades o dudas específicas.
--- Objetivos de aprendizaje.
--- Estilo de enseñanza preferido (visual, auditivo, kinestésico).

--Contexto (Psicológico: Estado emocional del usuario.)
--- Sentimientos actuales.
--- Situaciones estresantes o preocupantes.
--- Objetivos de bienestar emocional.
--- Preferencias de comunicación (formal, informal, empática).

--Contexto (Programación: Lenguajes o tecnologías de interés.)
--- Lenguajes de programación.
--- Proyectos o problemas específicos.
--- Nivel de experiencia.
--- Estilo de explicación preferido (detallado, conciso, con ejemplos).

----## Conclusión
Desarrollo con el apoyo de AI (intelligencia artificial) y el uso de modelos de lenguaje, se puede crear una aplicación de chat inteligente que se adapte a diferentes roles y contextos. Esto permitirá a los usuarios obtener respuestas personalizadas y relevantes según sus necesidades y preferencias, demostrando el potencial de la IA generativa en la mejora de la interacción humana.

--PERO : Cual es el rol del Humano?
-- EXPERTO EN EL TEMA: El humano puede ser un experto en el tema que se está discutiendo, proporcionando información adicional, corrigiendo errores o aclarando dudas que el modelo de lenguaje pueda tener.
