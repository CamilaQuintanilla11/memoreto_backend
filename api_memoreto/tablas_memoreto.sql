DROP TABLE IF EXISTS Session_has_memoreto;
DROP TABLE IF EXISTS Session;
DROP TABLE IF EXISTS Memoretos;
DROP TABLE IF EXISTS Niveles;
DROP TABLE IF EXISTS Usuario;

CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL, 
    rol TEXT NOT NULL CHECK (rol IN ('maestro', 'estudiante'))
);

CREATE TABLE Memoretos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel_dificultad INTEGER NOT NULL,
    nombre_memoreto TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    figuras TEXT NOT NULL,
    intersecciones TEXT NOT NULL
);

CREATE TABLE Niveles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_nivel TEXT NOT NULL,
    dificultad INTEGER NOT NULL
);

CREATE TABLE Session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

-- Datos de prueba para Usuario
INSERT INTO Usuario (name, token, rol) VALUES 
('Aldo', 'token_aldo_1', 'estudiante'),
('Maria', 'token_maria_2', 'estudiante'),
('Profe Juan', 'token_profe_1', 'maestro');

-- Datos de prueba para Niveles
INSERT INTO Niveles (nombre_nivel, dificultad) VALUES 
('Nivel Basico', 1),
('Nivel Intermedio', 2);

-- Datos de prueba para Memoretos
INSERT INTO Memoretos (nivel_dificultad, nombre_memoreto, descripcion, figuras, intersecciones) VALUES 
(1, 'Memoreto 1', 'Dificultad baja', '[1,2]', '[0]'),
(2, 'Memoreto 2', 'Dificultad media', '[3,4]', '[1,2]');

-- Datos de prueba para Session
INSERT INTO Session (id_usuario, id_nivel, score, tiempo_segundos, aciertos, errores) VALUES 
(1, 1, 850, 120, 10, 2),
(2, 1, 900, 95, 12, 0),
(1, 2, 600, 200, 8, 5);

-- Datos de prueba para Session_has_memoreto
INSERT INTO Session_has_memoreto (id_session, id_memoreto, score) VALUES 
(1, 1, 850),
(2, 1, 900),
(3, 2, 600);