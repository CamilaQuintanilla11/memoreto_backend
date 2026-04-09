import os
import sqlite3
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    def get_db_connection():
        db_path = os.path.join(os.path.dirname(__file__), "db_memoreto.sqlite")
        conn = sqlite3.connect(db_path)
        return conn

    @app.route("/")
    def home():
        return jsonify({"success": True, "message": "API de Memoreto funcionando"})

    # =========================
    # MEMORETOS
    # =========================

    @app.route("/memoretos", methods=["POST"])
    def obtener_memoreto_jugable():
        dificultad = request.form.get("dificultad")
        id_usuario = request.form.get("id_usuario")  # se recibe aunque ahorita no se use

        if not dificultad:
            return jsonify({"success": False, "mensaje": "Falta opción de 'dificultad'"}), 400

        if dificultad == "facil":
            id_nivel = 1
        elif dificultad == "medio":
            id_nivel = 2
        elif dificultad == "dificil":
            id_nivel = 3
        else:
            return jsonify({"success": False, "mensaje": "Dificultad no válida"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, id_nivel, nombre_memoreto, descripcion, figuras_json, valores_fichas
            FROM Memoreto
            WHERE id_nivel = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (id_nivel,))

        fila = cursor.fetchone()
        conn.close()

        if not fila:
            return jsonify({"success": False, "mensaje": "No hay memoretos para ese nivel"}), 404

        figuras = json.loads(fila[4]) if fila[4] else []

        memoreto = {
            "id": fila[0],
            "name": fila[2],
            "instruction": fila[3],
            "shapes": figuras,
            "level": fila[1],
            "valores_fichas": fila[5]
        }

        return jsonify({
            "success": True,
            "memoreto": memoreto
        })

    @app.route("/memoretos", methods=["GET"])
    def obtener_memoretos():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, id_nivel, nombre_memoreto, descripcion
            FROM Memoreto
        """)

        resultados = cursor.fetchall()
        conn.close()

        memoretos = []
        for fila in resultados:
            memoretos.append({
                "id": fila[0],
                "id_nivel": fila[1],
                "nombre_memoreto": fila[2],
                "descripcion": fila[3]
            })

        return jsonify({"success": True, "memoretos": memoretos})

    @app.route("/memoretos/<int:id>", methods=["GET"])
    def obtener_memoreto_por_id(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, id_nivel, nombre_memoreto, descripcion, figuras_json, valores_fichas
            FROM Memoreto
            WHERE id = ?
        """, (id,))

        memoreto = cursor.fetchone()
        conn.close()

        if not memoreto:
            return jsonify({"success": False, "mensaje": "Memoreto no encontrado"}), 404

        return jsonify({
            "success": True,
            "memoreto": {
                "id": memoreto[0],
                "id_nivel": memoreto[1],
                "nombre_memoreto": memoreto[2],
                "descripcion": memoreto[3],
                "shapes": json.loads(memoreto[4]) if memoreto[4] else [],
                "valores_fichas": memoreto[5]
            }
        })

    @app.route("/memoretos/<int:id>", methods=["PUT"])
    def actualizar_memoreto(id):
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Memoreto
            SET nombre_memoreto = ?, descripcion = ?, figuras_json = ?, valores_fichas = ?, id_nivel = ?
            WHERE id = ?
        """, (
            data["nombre_memoreto"],
            data["descripcion"],
            json.dumps(data.get("shapes", [])),
            data.get("valores_fichas"),
            data["id_nivel"],
            id
        ))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Memoreto actualizado correctamente"})

    @app.route("/memoretos/<int:id>", methods=["DELETE"])
    def eliminar_memoreto(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Memoreto
            WHERE id = ?
        """, (id,))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Memoreto eliminado correctamente"})

    @app.route("/niveles/<int:id_nivel>/memoretos", methods=["GET"])
    def obtener_memoretos_por_nivel(id_nivel):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombre_memoreto, descripcion, figuras_json, valores_fichas
            FROM Memoreto
            WHERE id_nivel = ?
        """, (id_nivel,))

        memoretos = cursor.fetchall()
        conn.close()

        memoreto_lista = []
        for fila in memoretos:
            memoreto_lista.append({
                "id": fila[0],
                "name": fila[1],
                "instruction": fila[2],
                "shapes": json.loads(fila[3]) if fila[3] else [],
                "valores_fichas": fila[4]
            })

        return jsonify({"success": True, "memoretos": memoreto_lista})

    # =========================
    # USUARIOS
    # =========================

    @app.route("/usuarios/<int:id>", methods=["GET"])
    def obtener_usuario(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, rol
            FROM Usuario
            WHERE id = ?
        """, (id,))

        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "id": user[0],
                "name": user[1],
                "rol": user[2]
            })
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404

    @app.route("/validausuario", methods=["POST"])
    def valida_usuario():
        data = request.get_json(silent = True)

        if not data:
            return jsonify({"success": False, "mensaje": "No se recibieron datos JSON"}), 400
            
        correo = data.get("correo") or data.get("data1")
        token = data.get("token") or data.get("data2")

        
        if not correo or not token:
            return jsonify({"success": False, "mensaje": "Faltan datos"}), 400

        conn = get_db_connection()
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
                "success": True,
                "id_usuario": user[0],
                "name": user[1],
                "rol": user[2],
                "token": user[3]
            })
        else:
            return jsonify({"success": False, "mensaje": "Credenciales inválidas"}), 401
        

    @app.route("/usuarios", methods=["POST"])
    def crear_usuario():
        data = request.get_json()

        nombre = data.get("name")
        correo = data.get("correo")
        token = data.get("token")
        rol = data.get("rol", "estudiante")
        grupo = data.get("grupo")

        if not nombre or not correo or not token:
            return jsonify({"success": False, "mensaje": "Faltan datos"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM Usuario
            WHERE name = ? OR correo = ?
        """, (nombre, correo))
        existente = cursor.fetchone()

        if existente:
            conn.close()
            return jsonify({"success": False, "mensaje": "El usuario o correo ya existe"}), 400

        cursor.execute("""
            INSERT INTO Usuario (name, correo, token, rol, grupo)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, correo, token, rol, grupo))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Usuario creado correctamente"})

    @app.route("/usuarios/<int:id>", methods=["PUT"])
    def actualizar_usuario(id):
        data = request.get_json()

        campo_actualizar = []
        datos = []

        if "name" in data:
            campo_actualizar.append("name = ?")
            datos.append(data["name"])
        
        if "correo" in data:
            campo_actualizar.append("correo = ?")
            datos.append(data["correo"])

        if "token" in data:
            campo_actualizar.append("token = ?")
            datos.append(data["token"])

        if "rol" in data:
            campo_actualizar.append("rol = ?")
            datos.append(data["rol"])

        if "grupo" in data:
            campo_actualizar.append("grupo = ?")
            datos.append(data["grupo"])

        if not campo_actualizar:
            return jsonify({"success": False, "mensaje": "No hay datos para actualizar"}), 400

        query = f"""
            UPDATE Usuario
            SET {', '.join(campo_actualizar)}
            WHERE id = ?
        """
        datos.append(id)
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(query, datos)

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Usuario actualizado correctamente"})

    @app.route("/usuarios/<int:id>", methods=["DELETE"])
    def eliminar_usuario(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Usuario
            WHERE id = ?
        """, (id,))

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Usuario eliminado correctamente"})

    # =========================
    # PUNTAJES / SESSION
    # =========================

    @app.route("/puntajes", methods=["POST"])
    def crear_puntaje():
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Session (id_usuario, id_nivel, id_reto, tiempo_segundos, score, aciertos, errores)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id_usuario"],
            data["id_nivel"],
            data["id_reto"],
            data["tiempo_segundos"],
            data["score"],
            data.get("aciertos", 0),
            data.get("errores", 0)
        ))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Puntaje guardado"})

    @app.route("/puntajes", methods=["GET"])
    def consultar_puntajes():
        conn = get_db_connection()
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

        return jsonify({
            "success": True,
            "total_resultados": len(historial),
            "historial": historial
        })

    @app.route("/puntajes/<int:id>", methods=["PUT"])
    def actualizar_puntaje(id):
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Session
            SET score = ?
            WHERE id = ?
        """, (data["score"], id))

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Puntaje actualizado correctamente"})

    @app.route("/puntajes/<int:id>", methods=["DELETE"])
    def eliminar_puntaje(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Session
            WHERE id = ?
        """, (id,))

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Puntaje eliminado correctamente"})

    # =========================
    # NIVELES
    # =========================

    @app.route("/niveles", methods=["GET"])
    def obtener_niveles():
        conn = get_db_connection()
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

    @app.route("/niveles", methods=["POST"])
    def crear_nivel():
        data = request.get_json()
        nombre_nivel = data.get("nombre_nivel")
        dificultad = data.get("dificultad")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Niveles (nombre_nivel, dificultad)
            VALUES (?, ?)
        """, (nombre_nivel, dificultad))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Nivel creado exitosamente"})

    @app.route("/niveles/<int:id>", methods=["PUT"])
    def actualizar_nivel(id):
        data = request.get_json()
        nombre_nivel = data.get("nombre_nivel")
        dificultad = data.get("dificultad")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Niveles
            SET nombre_nivel = ?, dificultad = ?
            WHERE id = ?
        """, (nombre_nivel, dificultad, id))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Nivel actualizado exitosamente"})

    @app.route("/niveles/<int:id>", methods=["DELETE"])
    def eliminar_nivel(id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Niveles
            WHERE id = ?
        """, (id,))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "mensaje": "Nivel eliminado exitosamente"})

    # =========================
    # DASHBOARD
    # =========================

    @app.route("/api/graficas", methods=["GET"])
    def obtener_datos_graficas():
        conn = get_db_connection()
        cursor = conn.cursor()

        grupo = request.args.get("grupo")

        cursor.execute("""
            SELECT n.nombre_nivel, AVG(s.tiempo_segundos) as prom_tiempo, AVG(s.score) as prom_score
            FROM Session s
            JOIN Niveles n ON s.id_nivel = n.id
            GROUP BY n.nombre_nivel
        """)
        resultados1 = cursor.fetchall()

        cursor.execute("""
            SELECT AVG(aciertos) as prom_aciertos, AVG(errores) as prom_errores
            FROM Session
        """)
        resultados2 = cursor.fetchone()

        cursor.execute("""
            SELECT n.nombre_nivel, s.score
            FROM Session s
            JOIN Niveles n ON s.id_nivel = n.id
        """)
        resultados3 = cursor.fetchall()

        cursor.execute("""
            SELECT u.grupo, 
                    AVG(score) as prom_score, AVG(tiempo_segundos) as prom_tiempo,
                    COUNT(*) as total_jugadas
            FROM Session s
            JOIN Usuario u ON s.id_usuario = u.id
            WHERE u.grupo IS NOT NULL
            AND (? IS NULL OR u.grupo = ?)
            GROUP BY u.grupo
        """, (grupo, grupo))
        resultados4 = cursor.fetchall()

        conn.close()

        niveles = [fila[0] for fila in resultados1]
        tiempos = [fila[1] for fila in resultados1]
        scores = [fila[2] for fila in resultados1]

        prom_aciertos = resultados2[0] if resultados2 else 0
        prom_errores = resultados2[1] if resultados2 else 0

        distribucion = []
        for fila in resultados3:
            distribucion.append({
                "nivel": fila[0],
                "score": fila[1]
            })
        
        grupos = []
        promedios_grupo = []
        tiempos_grupo = []
        partidas_grupo = []

        for fila in resultados4:
            grupos.append(fila[0])
            promedios_grupo.append(fila[1])
            tiempos_grupo.append(fila[2])
            partidas_grupo.append(fila[3])

        return jsonify({
            "success": True,
            "promedios_por_nivel": {
                "niveles": niveles,
                "tiempos": tiempos,
                "scores": scores
            },
            "aciertos_vs_errores": {
                "prom_aciertos": prom_aciertos,
                "prom_errores": prom_errores
            },
            "distribucion_puntajes": distribucion,

            "rendimiento_por_grupo": {
                "grupos": grupos,
                "promedios_score": promedios_grupo,
                "promedios_tiempo": tiempos_grupo,
                "total_partidas": partidas_grupo
            }
        })
    
    @app.route("/debug/memoretos")
    def debug_memoretos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Memoreto")
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)