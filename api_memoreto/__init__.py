import os
from flask import Flask, request
from markupsafe import escape #Evitar inyecciones de código en las rutas

def create_app(test_config=None):
    # Inicializacion de la aplicacion Flask
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        # DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # --- ENDPOINT 1: Validación de usuario GET ---
    @app.route("/docs/validausuario", methods=['GET'])
    def docs_valida_usuario():
        return {
            "nombre": "Validación de usuario",
            "descripcion": "Este servicio permite validar si un usuario estudiante o docente ya ha sido registrado previamente y sus credenciales son correctas.",
            "url": "/validausuario",
            "metodo_http": "POST",
            "parametros_entrada": {"usuario": "alumnoabc@tec.mx", "pass": "12345678"},
            "parametros_salida": {"valido": True, "id_usuario": 10, "rol": "estudiante"}
        }

    # ---  Funcionalidad de validación de usuario POST ---
    @app.route("/validausuario", methods=['POST'])
    def valida_usuario():
        return {"valido": True, "id_usuario": 10, "rol": "estudiante"}
    
    # --- ENDPOINT 2: Crear puntaje POST ---
    @app.route("/puntaje", methods=['POST']) # nombre corregido 
    def crear_puntaje(): 
        return {"success": True,  
        "id_usuario" : 10,
        "id_reto": 1,
        "tiempo_segundos": 1,
        "mensaje": "Puntaje guardado",
        "historial": [
        {
            "id_partida": 1,
            "id_reto": 10,
            "puntaje": 100,
            "fecha": "23-02-26"
        }]}


    # --- ENDPOINT 3: Consulta de puntaje de usuario  GET ---    
    @app.route("/usuarios/<int:id_usuario>/puntajes", methods=['GET'])
    def consultar_puntajes_usuario(id_usuario):
        return {"success": True,  
        "id_usuario": id_usuario,
        "historial": [
        {
            "id_partida": 1,
            "id_reto": 10,
            "puntaje": 100,
            "fecha": "23-02-26"
        }]} 

    # --- ENDPOINT 4: Consulta de puntajes por reto GET ---

    @app.route("/retos/<int:id_reto>/puntajes", methods=['GET'])
    def consultar_puntajes_reto(id_reto):
        return {"success": True,  
        "id_reto": id_reto,
        "historial": [
        {
            "id_partida": 9,
            "id_usuario": 1,
            "puntaje": 500,
            "fecha": "23-02-26"
            },
        {   
            "id_partida": 10,
            "id_usuario": 4,
            "puntaje": 900,
            "fecha": "23-02-26"
        }]} 


    # --- ENDPOINT 5: Actualizar puntaje PUT ---
    @app.route("/actualizarpuntaje/<id>", methods=["PUT"])
    def actualizar_puntaje(id): # Recibe el id del puntaje desde la URL
        data = request.get_json() # Obtiene los datos que se enviaron en formato JSON desde el cliente
        return {
            "mensaje" : "Puntaje actualizado correctamente", # Devuelve un mensaje de confirmación
            "id" : id,
            "nuevo_valor" : data
        }
    

    # --- ENDPOINT 6: Eliminar puntaje DELETE ---
    @app.route("/eliminarpuntaje/<id>", methods=["DELETE"])
    def eliminar_puntaje(id): # Recibe el id del puntaje desde la URL
        return {
            "mensaje": "Puntaje eliminado correctamente",
            "id": id # y devuelve un mensaje confirmando que el registro fue eliminado
        }

    return app