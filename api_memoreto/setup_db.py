import sqlite3
import os

def inicializar_bd():

    DB_PATH = os.path.join(os.path.dirname(__file__), "db_memoreto.sqlite")

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    sql_path = os.path.join(os.path.dirname(__file__), "tablas_memoreto.sql")

    with open(sql_path, "r", encoding="utf-8", errors="ignore") as archivo_sql:
        script = archivo_sql.read()

    try:
        cursor.executescript(script)
    except Exception as e:
        print("ERROR EN SQL:")
        print(e)

    conexion.commit()
    conexion.close()

    print("DB creada correctamente en:", DB_PATH)


if __name__ == '__main__':
    inicializar_bd()