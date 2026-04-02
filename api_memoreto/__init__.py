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

    #USUARIO !!

    @app.route("/usuarios/<int:id>", methods=['GET'])
    def obtener_usuario(id):
        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, rol 
            FROM Usuario
            WHERE id = ?
        """, (id))
        user = cursor.fetchone()
        conn.close()

        if user:
            return {"id": user[0], "name": user[1], "rol": user[2]}
        else:
            return {"error": "Usuario no encontrado"}

    # ---  Funcionalidad de validación de usuario POST ---
    @app.route("/validausuario", methods=['POST'])
    def valida_usuario():
        data = request.get_json()

        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, rol FROM Usuario WHERE token = ?
        """, (data["token"],))
        user = cursor.fetchone()
        conn.close()

        if user:
            return {"success": True, "id_usuario": user[0], "rol": user[1]}
        else:
            return {"success": False, "mensaje": "Credenciales inválidas"}
        

    @app.route("/usuarios", methods=['POST'])
    def crear_usuario():
        data = request.get_json()

        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Usuario (name, token, rol)
            VALUES (?,?,?)
        """, (data["name"], data["token"], data["rol"]))
        conn.commit()
        conn.close()

        return {"mensaje": "Usuario creado correctamente"}

    @app.route("/usuarios/<int:id>", methods=['PUT'])
    def actualizar_usuario(id):
        data = request.get_json()
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Usuario
            SET name = ?
            WHERE id = ?
        """, (data["name"], id))
        conn.commit()
        conn.close()

        return {"mensaje": "Usuario actualizado correctamente"}
    
    @app.route("/usuarios/<id>", methods=['DELETE'])
    def eliminar_usuario(id):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Usuario
            WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()

        return {"mensaje": "Usuario eliminado correctamente"}

    #SESSION !!
    # --- ENDPOINT 2: Crear puntaje POST ---
    @app.route("/puntajes", methods=['POST'])  
    def crear_puntaje(): 
        data = request.get_json()

        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Session (id_usuario, id_nivel, id_reto, tiempo_segundos, score, aciertos, errores)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data["id_usuario"], data["id_nivel"], data["id_reto"], data["tiempo_segundos"], data["score"], data.get("aciertos"), data.get("errores")))
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
            SELECT id, id_reto, id_nivel, tiempo_segundos, score, fecha
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
                "id_usuario": fila[0],
                "id_reto": fila[1],
                "id_nivel": fila[2],
                "tiempo_segundos": fila[3],
                "score": fila[4],
                "fecha": fila[5]
            })

        return {"succes": True, "historial": historial}


    # --- ENDPOINT 4: Consulta de puntajes por reto GET ---

    @app.route("/retos/<int:id_reto>/puntajes", methods=['GET']) # corregir nombre ruta
    def consultar_puntajes_reto(id_reto):
        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, id_usuario, score, fecha
            FROM Session
            WHERE id_reto = ?
            ORDER BY score DESC
            LIMIT ?
        """, (id_reto, request.args.get("limit", default=20, type=int)))
        resultados = cursor.fetchall()
        conn.close()    

        historial = []
        for fila in resultados:
            historial.append({
                "id_partida": fila[0],
                "id_usuario": fila[1],
                "puntaje": fila[2],
                "fecha": fila[3]
            })

        return {"success": True, "historial": historial}



    # --- ENDPOINT 5: Actualizar puntaje PUT ---
    @app.route("/puntajes/<id>", methods=["PUT"]) 
    def actualizar_puntaje(id): # Recibe el id del puntaje desde la URL
        data = request.get_json() # Obtiene los datos que se enviaron en formato JSON desde el cliente

        conn = sqlite3.connect('db_memoreto.sqlite') # Conecta a la base de datos
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Session
            SET score = ?
            WHERE id = ?
        """, (data["score"], id))
        conn.commit()
        conn.close()

        return {"mensaje" : "Puntaje actualizado correctamente"}
    

    # --- ENDPOINT 6: Eliminar puntaje DELETE ---
    @app.route("/puntajes/<id>", methods=["DELETE"])
    def eliminar_puntaje(id): # Recibe el id del puntaje desde la URL
        conn = sqlite3.connect('db_memoreto.sqlite') 
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Session
            WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()

        return {"mensaje": "Puntaje eliminado correctamente"}

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