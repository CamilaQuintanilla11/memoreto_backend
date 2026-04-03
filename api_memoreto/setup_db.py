import sqlite3

def inicializar_bd():
    # Conecta o crea el archivo de la base de datos
    conexion = sqlite3.connect('db_memoreto.sqlite')
    cursor = conexion.cursor()
    
    # Lee el archivo SQL con las tablas
    with open('tablas_memoreto.sql', 'r', encoding='utf-8') as archivo_sql:
        script = archivo_sql.read()
        
    # Ejecuta el script para crear las tablas
    cursor.executescript(script)
    
    # Inserta el usuario de prueba de su documentación (Endpoint 1)
    # Nota: En un proyecto real la contraseña iría encriptada (hash), 
    # pero para esta fase de pruebas la dejamos en texto plano.
    #cursor.execute("""
    #    INSERT INTO usuario (correo, password, rol) 
    #    VALUES ('alumnoabc@tec.mx', '12345678', 'estudiante')
    #""")
    
    conexion.commit()
    conexion.close()
    print("¡Base de datos 'db_memoreto.sqlite' inicializada correctamente con el usuario de prueba!")

if __name__ == '__main__':
    inicializar_bd()