import os
import sqlite3
import json
import random
from flask import Flask, request, jsonify
from flask_cors import CORS 
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

    @app.route("/")
    def home():
        return jsonify({"success": True, "message": "API de Memoreto funcionando"})
    #ENDPOINT: POST memoretos
    @app.route("/memoretos", methods=["POST"])
    def obtener_memoreto_jugable():
        data = request.get_json()
        if not data or "dificultad" not in data:
            return {"success": False, "mensaje": "Falta opción de 'dificultad'"}, 400
        dificultad = data.get("dificultad")

        if dificultad == "facil":
            id_nivel = 1
        elif dificultad == "medio":
            id_nivel = 2
        elif dificultad == "dificil":
            id_nivel = 3
        else:
            return {"success": False, "mensaje": "Dificultad no válida"}, 400

        db_path = os.path.join(os.path.dirname(__file__), "db_memoreto.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, id_nivel, nombre_memoreto, descripcion, figuras_json, intersecciones_json
            FROM Memoreto
            WHERE id_nivel = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (id_nivel,))

        fila = cursor.fetchone()
        conn.close()

        if not fila:
            return {"success": False, "mensaje": "No hay memoretos para ese nivel"}, 404

        figuras = json.loads(fila[4])
        intersecciones = json.loads(fila[5])

        memoreto = {
            "id": fila[0],
            "descripcion": fila[3],
            "shapes": figuras,
            "intersections": intersecciones,
            "level": fila[1]
        }

        return jsonify({"success": True, "memoreto": memoreto})

    #ENDPOINT: PUT memoretos
    @app.route("/memoretos/<int:id>", methods=["PUT"])
    def actualizar_memoreto(id):
        data = request.get_json()
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Memoreto
            SET nombre_memoreto = ?, descripcion = ?, figuras_json = ?, intersecciones_json = ?, id_nivel = ?
            WHERE id = ?
        """, (data["nombre_memoreto"], data["descripcion"], json.dumps(data.get("shapes", [])), json.dumps(data.get("intersections", [])), data["id_nivel"], id))
        conn.commit()
        conn.close()

        return jsonify({"success": True,"mensaje": "Memoreto actualizado correctamente"})
    #ENDPOINT: DELETE memoretos
    @app.route("/memoretos/<int:id>", methods=["DELETE"])
    def eliminar_memoreto(id):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Memoreto 
            WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True,"mensaje": "Memoreto eliminado correctamente"})


    #USUARIO !!

    @app.route("/usuarios/<int:id>", methods=['GET'])
    def obtener_usuario(id):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, rol 
            FROM Usuario
            WHERE id = ?
        """, (id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({"id": user[0], "name": user[1], "rol": user[2]})
        else:
            return jsonify({"error": "Usuario no encontrado"})

    # ---  Funcionalidad de validación de usuario POST ---
    @app.route("/validausuario", methods=['POST'])
    def valida_usuario():
        data = request.get_json()
        if not data or "correo" not in data or "token" not in data:
            return jsonify({"success": False, "mensaje": "Faltan 'correo' o 'token'"}), 400
        correo = data.get("correo")
        token = data.get("token")

        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, rol, token
            FROM Usuario 
            WHERE correo = ? AND token = ?
        """, (correo, token))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "success":True,
                "id_usuario": user[0],
                "name": user[1],
                "rol": user[2],
                "token": user[3]
            })
        else:
            return jsonify({"success": False, "mensaje": "Credenciales inválidas"}), 401
        

    @app.route("/usuarios", methods=['POST'])
    def crear_usuario():
        data = request.get_json()

        nombre = data.get("name")
        correo = data.get("correo")
        token = data.get("token")
        rol = data.get("rol", "estudiante")

        if not nombre or not correo or not token:
            return jsonify({"success": False, "mensaje": "Faltan datos"}), 400

        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        
        # revisar si ya existe el usuario o correo
        cursor.execute("""
            SELECT id FROM Usuario
            WHERE name = ? OR correo = ?
        """, (nombre, correo))
        existente = cursor.fetchone()

        if existente:
            conn.close()
            return jsonify({"success": False, "mensaje": "El usuario o correo ya existe"}), 400

        cursor.execute("""
            INSERT INTO Usuario (name, correo, token, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, correo, token, rol))
        
        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Usuario creado correctamente"})

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

        return jsonify({"mensaje": "Usuario actualizado correctamente"})
    
    @app.route("/usuarios/<int:id>", methods=['DELETE'])
    def eliminar_usuario(id):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Usuario
            WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Usuario eliminado correctamente"})

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
        return jsonify({"success": True,"mensaje": "Puntaje guardado"})


    @app.route("/puntajes", methods=['GET'])
    def consultar_puntajes():
        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        id_usuario = request.args.get("id_usuario", type=int)
        id_reto = request.args.get("id_reto", type=int)
        limit = request.args.get("limit", default=20, type=int)

        query = """
            SELECT id, id_usuario, id_nivel, id_reto, tiempo_segundos, score, aciertos, errores, fecha
            FROM Session
            WHERE 1=1
        """ 
        params = []

        if id_usuario:
            query += " AND id_usuario = ?"
            params.append(id_usuario)
        if id_reto:
            query += " AND id_reto = ?"
            params.append(id_reto)

        query += " ORDER BY fecha DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return jsonify({"success": False, "mensaje": "No se encontraron puntajes"}), 404

        historial = []
        for fila in resultados:
            historial.append({
                "id": fila[0],
                "id_usuario": fila[1],
                "id_nivel": fila[2],
                "id_reto": fila[3],
                "tiempo_segundos": fila[4],
                "score": fila[5],
                "aciertos": fila[6],
                "errores": fila[7],
                "fecha": fila[8]
            })

        return jsonify({"success": True, "total_resultados": len(historial), "historial": historial})
    
    # --- ENDPOINT 3: Consulta de puntaje de usuario  GET ---
    @app.route("/usuarios/<int:id_usuario>/puntajes", methods=['GET']) # corregir nombre ruta
    def consultar_puntajes_usuario(id_usuario):
        
        db_path = os.path.join(os.path.dirname(__file__), 'db_memoreto.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, id_reto, id_nivel, tiempo_segundos, score, aciertos, errores, fecha
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
                "id_session": fila[0],
                "id_reto": fila[1],
                "id_nivel": fila[2],
                "tiempo_segundos": fila[3],
                "score": fila[4],
                "aciertos": fila[5],
                "errores": fila[6],
                "fecha": fila[7]
            })

        return jsonify({"success": True, "historial": historial})


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
                "id_session": fila[0],
                "id_usuario": fila[1],
                "score": fila[2],
                "fecha": fila[3]
            })

        return jsonify({"success": True, "historial": historial})



    # --- ENDPOINT 5: Actualizar puntaje PUT ---
    @app.route("/puntajes/<int:id>", methods=["PUT"]) 
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

        return jsonify({"mensaje" : "Puntaje actualizado correctamente"})
    

    # --- ENDPOINT 6: Eliminar puntaje DELETE ---
    @app.route("/puntajes/<int:id>", methods=["DELETE"])
    def eliminar_puntaje(id): # Recibe el id del puntaje desde la URL
        conn = sqlite3.connect('db_memoreto.sqlite') 
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Session
            WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Puntaje eliminado correctamente"})
    
    #MEMORETO !!!
    # ENDPOINT: obtener lista de memoretos GET
    @app.route("/memoretos", methods=['GET'])
    def obtener_memoretos():
        DB_PATH = os.path.join(os.path.dirname(__file__), "db_memoreto.sqlite")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, id_nivel, nombre_memoreto, descripcion
            FROM Memoreto
        """)
        resultados = cursor.fetchall()
        conn.close()

        memoreto = []
        for fila in resultados:
            memoreto.append({
                "id": fila[0],
                "id_nivel": fila[1],
                "nombre_memoreto": fila[2],
                "descripcion": fila[3]
            })
        return jsonify({"success": True, "memoretos": memoreto})
    
    #ENDPOINT: obtener memoreto por id GET
    @app.route("/memoretos/<int:id>", methods= ['GET'])
    def obtener_memoreto_por_id(id):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, id_nivel, nombre_memoreto, descripcion
            FROM Memoreto
            WHERE id = ?
        """, (id,))
        memoreto = cursor.fetchone()
        conn.close()
    
        if memoreto:
            return jsonify({
                "success": True,
                "memoreto": {
                    "id": memoreto[0],
                    "id_nivel": memoreto[1],
                    "nombre_memoreto": memoreto[2],
                    "descripcion": memoreto[3]
                }
            })
        else:
            return jsonify({"success": False, "mensaje": "Memoreto no encontrado"})
        
    #ENDPOINT: obtener lista de memoretos por nivel GET
    @app.route("/niveles/<int:id_nivel>/memoretos", methods=['GET'])
    def obtener_memoretos_por_nivel(id_nivel):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre_memoreto, descripcion, figuras_json, intersecciones_json
            FROM Memoreto
            WHERE id_nivel = ?
        """, (id_nivel,))
        memoreto = cursor.fetchall()
        conn.close()

        memoreto_lista = []
        for fila in memoreto:
            memoreto_lista.append({
                "id": fila[0],
                "nombre_memoreto": fila[1],
                "descripcion": fila[2],
                "shapes": json.loads(fila[3]),
                "intersections": json.loads(fila[4])
            })

        return jsonify({"success": True, "memoretos": memoreto_lista})
        


    #ENDPOINT: obtener lista completa de niveles GET
    @app.route("/niveles", methods= ['GET'])
    def obtener_niveles():
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre_nivel, dificultad
            FROM Niveles
        """)
        niveles = cursor.fetchall()
        conn.close()

        niveles_lista = []
        for fila in niveles:
            niveles_lista.append({
                "id": fila[0],
                "nombre_nivel": fila[1],
                "dificultad": fila[2]
            })

        return jsonify({"success": True, "niveles": niveles_lista})
    
    #ENDPOINT: POST niveles
    @app.route("/niveles", methods=['POST'])
    def crear_nivel():
        data = request.get_json()
        nombre_nivel = data.get("nombre_nivel")
        dificultad = data.get("dificultad")

        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Niveles (nombre_nivel, dificultad)
            VALUES (?, ?)
        """, (nombre_nivel, dificultad))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Nivel creado exitosamente"})

    #ENDPOINT: PUT niveles
    @app.route("/niveles/<int:id>", methods= ['PUT'])
    def actualizar_nivel(id):
        data = request.get_json()
        nombre_nivel = data.get("nombre_nivel")
        dificultad = data.get("dificultad")

        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Niveles
            SET nombre_nivel = ?, dificultad = ?
            WHERE id = ?
        """, (nombre_nivel, dificultad, id))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Nivel actualizado exitosamente"})
    #ENDPOINT: DELETE niveles
    @app.route("/niveles/<int:id>", methods= ['DELETE'])
    def eliminar_nivel(id):
        conn = sqlite3.connect('db_memoreto.sqlite')
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Niveles
            WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Nivel eliminado exitosamente"})

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
        
        return jsonify({
            "success": True,
            "niveles": niveles,
            "tiempos": tiempos,
            "scores": scores
        })
    
    return app



if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)