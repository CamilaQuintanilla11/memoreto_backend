DROP TABLE IF EXISTS Session;
DROP TABLE IF EXISTS Memoreto;
DROP TABLE IF EXISTS Niveles;
DROP TABLE IF EXISTS Usuario;

CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    token TEXT UNIQUE NOT NULL, 
    rol TEXT NOT NULL CHECK (rol IN ('maestro', 'estudiante')),
    grupo TEXT 
);

CREATE TABLE Memoreto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_nivel INTEGER NOT NULL,
    nombre_memoreto TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    figuras_json TEXT NOT NULL,
    intersecciones_json TEXT NOT NULL,
    FOREIGN KEY (id_nivel) REFERENCES Niveles(id)
);

CREATE TABLE Niveles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_nivel TEXT NOT NULL,
    dificultad INTEGER NOT NULL
);

CREATE TABLE Session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_reto INTEGER NOT NULL,
    id_nivel INTEGER NOT NULL,         
    score INTEGER NOT NULL,            
    tiempo_segundos INTEGER NOT NULL,  
    aciertos INTEGER DEFAULT 0,        
    errores INTEGER DEFAULT 0,         
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_nivel) REFERENCES Niveles(id),
    FOREIGN KEY (id_reto) REFERENCES Memoreto(id)
);

-- Datos de prueba para Usuario
INSERT INTO Usuario (name, correo, token, rol) VALUES 
('Aldo', 'aldo@mail.com', '84edde57740fd5953d62b720ccf5e8f4', 'estudiante'),
('Maria', 'maria@mail.com', '683cf42782096456d4d64c2f9fe2f8cb', 'estudiante'),
('Profe Juan', 'profejuan@mail.com', '9b776daefefc486d19b11472695985f3', 'maestro');

-- Datos de prueba para Niveles
INSERT INTO Niveles (nombre_nivel, dificultad) VALUES 
('Nivel Basico', 1),
('Nivel Intermedio', 2),
('Nivel Dificil', 3);

-- Datos de prueba para Memoretos
-- Datos de prueba para Memoretos con ID manual
INSERT INTO Memoreto (id, id_nivel, nombre_memoreto, descripcion, figuras_json, intersecciones_json) VALUES 
(
    1,
    1,
    'Memoreto facil 3 circulos',
    'Usa los números del 1 al 6 sin repetir. Todas las figuras deben sumar lo mismo.',
    '[{"id":1,"center":[-1.0,0.9,0],"size":[3.0,3.0,0.1],"type":"circle","rotation":[0,0,0]},{"id":2,"center":[1.0,0.9,0],"size":[3.0,3.0,0.1],"type":"circle","rotation":[0,0,0]},{"id":3,"center":[0,-0.4,0],"size":[3.0,3.0,0.1],"type":"circle","rotation":[0,0,0]}]',
    '[]'
),
(
    2,
    2,
    'Memoreto medio rectangulos y circulo',
    'Se han dibujado dos rectangulos y un circulo, generando 12 puntos de corte...',
    '[{"id":1,"center":[0,0,0],"size":[6.4,6.4,0.1],"type":"circle","rotation":[0,0,0]},{"id":2,"center":[0,0,0],"size":[5.8,2.8,0.1],"type":"square","rotation":[0,0,0]},{"id":3,"center":[0,0,0],"size":[2.8,5.8,0.1],"type":"square","rotation":[0,0,0]}]',
    '[]'
),
(
    4,
    2,
    'Memoreto medio elipse triangulo rectangulo',
    'Se han dibujado una elipse, un triangulo y un rectangulo...',
    '[{"id":1,"center":[0.0,-0.25,0],"size":[3.8,5.2,0.1],"type":"circle","rotation":[0,0,0]},
    {"id":2,"center":[0.0,0.15,0],"size":[4.8,4.8,0.1],"type":"triangle","rotation":[0,0,0]},
    {"id":3,"center":[0.0,-0.05,0],"size":[5.6,2.2,0.1],"type":"square","rotation":[0,0,0]}]',
    '[]'
),
(
    3,
    3,
    'Memoreto dificil prueba',
    'En el grafico hay tres circulos y un triangulo...',
    '[{"id":1,"center":[-1.33,0.98,0],"size":[3.36,3.36,0.1],"type":"circle","rotation":[0,0,0]},
    {"id":2,"center":[1.33,0.98,0],"size":[3.36,3.36,0.1],"type":"circle","rotation":[0,0,0]},
    {"id":3,"center":[0,-0.84,0],"size":[3.36,3.36,0.1],"type":"circle","rotation":[0,0,0]},
    {"id":4,"center":[0,0.21,0],"size":[3.15,2.94,0.1],"type":"triangle","rotation":[0,0,180]}]',
    '[]'
);

-- Datos de prueba para Session
INSERT INTO Session (id_usuario, id_reto, id_nivel, score, tiempo_segundos, aciertos, errores) VALUES 
(1, 1, 1, 850, 120, 10, 2),
(2, 1, 1, 900, 95, 12, 0),
(1, 2, 2, 600, 200, 8, 5);

