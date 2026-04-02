import os
import sqlite3
from flask_cors import CORS 
from flask import Flask, request
from markupsafe import escape #Evitar inyecciones de código en las rutas

def create_app(test_config=None):
    # Inicializacion de la aplicacion Flask
    app = Flask(__name__, instance_relative_config=True)
    CORS(app) # Habilitar CORS para permitir solicitudes desde el frontend
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
            "usuario": "alumnoabc@tec.mx", 
            "pass": "12345678",
            "valido": True, 
            "id_usuario": 10, 
            "rol": "estudiante"
        }

    # ---  Funcionalidad de validación de usuario POST ---
    @app.route("/validausuario", methods=['POST'])
    def valida_usuario():
        return {"valido": True, "id_usuario": 10, "rol": "estudiante"}
    
    # --- ENDPOINT 2: Crear puntaje POST ---
    @app.route("/puntajes", methods=['POST'])  
    def crear_puntaje(): 
        data = request.get_json()

        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Session (id_usuario, id_reto, tiempo_segundos, score, aciertos, errores)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["id_usuario"], data["id_reto"], data["tiempo_segundos"], data["score"], data.get("aciertos"), data.get("errores")))
        conn.commit()
        conn.close()
        return {"success": True,"mensaje": "Puntaje guardado"}


    # --- ENDPOINT 3: Consulta de puntaje de usuario  GET ---    
    @app.route("/usuarios/<int:id_usuario>/puntajes", methods=['GET']) # corregir nombre ruta
    def consultar_puntajes_usuario(id_usuario):
        
        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_partida, id_reto, tiempo_segundos, score, fecha
            FROM Session
            WHERE id_usuario = ?
            Order BY fecha DESC
            LIMIT ?
        """, (id_usuario, request.args.get("limit", default=20, type=int)))
        resultados = cursor.fetchall()
        conn.close()

        historial = []
        for fila in resultados:
            historial.append({
                "id_partida": fila[0],
                "id_reto": fila[1],
                "tiempo_segundos": fila[2],
                "score": fila[3],
                "fecha": fila[4]
            })

        return {"succes": True, "historial": historial}


    # --- ENDPOINT 4: Consulta de puntajes por reto GET ---

    @app.route("/retos/<int:id_reto>/puntajes", methods=['GET']) # corregir nombre ruta
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
    @app.route("/puntajes/<id>", methods=["PUT"]) 
    def actualizar_puntaje(id): # Recibe el id del puntaje desde la URL
        data = request.get_json() # Obtiene los datos que se enviaron en formato JSON desde el cliente
        return {
            "mensaje" : "Puntaje actualizado correctamente", # Devuelve un mensaje de confirmación
            "id" : id,
            "nuevo_valor" : data
        }
    

    # --- ENDPOINT 6: Eliminar puntaje DELETE ---
    @app.route("/puntajes/<id>", methods=["DELETE"])
    def eliminar_puntaje(id): # Recibe el id del puntaje desde la URL
        return {
            "mensaje": "Puntaje eliminado correctamente",
            "id": id # y devuelve un mensaje confirmando que el registro fue eliminado
        }

    # --- ENDPOINT 7: Datos para el Dashboard (Gráficas) ---
    @app.route("/api/graficas", methods=['GET'])
    def obtener_datos_graficas():
        # Conectar a la base de datos (busca el archivo en esta misma carpeta)
        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Consulta SQL: Promedio de tiempo y puntaje por cada nivel
        query = """
            SELECT n.nombre_nivel, AVG(s.tiempo_segundos) as prom_tiempo, AVG(s.score) as prom_score
            FROM Session s
            JOIN Niveles n ON s.id_nivel = n.id
            GROUP BY n.nombre_nivel
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        
        # Separar los resultados en listas para mandarlos a la web
        niveles = [fila[0] for fila in resultados]
        tiempos = [fila[1] for fila in resultados]
        scores = [fila[2] for fila in resultados]
        
        return {
            "success": True,
            "niveles": niveles,
            "tiempos": tiempos,
            "scores": scores
        }

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)