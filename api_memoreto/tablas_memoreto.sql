DROP TABLE IF EXISTS Progreso;
DROP TABLE IF EXISTS Intentos;
DROP TABLE IF EXISTS Niveles;
DROP TABLE IF EXISTS Usuario;

CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL, 
    rol TEXT NOT NULL CHECK (rol IN ('maestro', 'estudiante'))
);
CREATE TABLE Memoretos {
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    nivel_dificultad INTEGER NOT NULL,
    nombre_memoreto TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    figuras INTEGER [] NOT NULL,
    intersecciones INTEGER [] NOT NULL,
}
CREATE TABLE Niveles (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre_nivel TEXT NOT NULL,
    dificultad INTEGER NOT NULL
);
CREATE TABLE Session (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_usuario INTEGER NOT NULL,
    id_nivel INTEGER NOT NULL,         
    score INTEGER NOT NULL,            
    tiempo_segundos INTEGER NOT NULL,  
    aciertos INTEGER DEFAULT 0,        
    errores INTEGER DEFAULT 0,         
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_nivel) REFERENCES Niveles(id)
);
CREATE TABLE Session_has_memoreto (
    id_session INTEGER NOT NULL,
    id_memoreto INTEGER NOT NULL,
    score INTEGER NOT NULL,          
    PRIMARY KEY (id_session, id_memoreto),
    FOREIGN KEY (id_session) REFERENCES Session(id),
    FOREIGN KEY (id_memoreto) REFERENCES Memoretos(id)
);