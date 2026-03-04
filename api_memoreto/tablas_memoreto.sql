DROP TABLE IF EXISTS Progreso;
DROP TABLE IF EXISTS Intentos;
DROP TABLE IF EXISTS Niveles;
DROP TABLE IF EXISTS Usuario;

-- 1. Tabla de Usuarios
CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    correo TEXT UNIQUE NOT NULL, 
    password TEXT NOT NULL,      
    rol TEXT NOT NULL
);

-- 2. Tabla del catálogo de niveles 
CREATE TABLE Niveles (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre_nivel TEXT NOT NULL,
    descripcion TEXT NOT NULL
);

-- 3. Tabla de Session 
CREATE TABLE Session (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    score INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    id_nivelActual INTEGER NOT NULL,
    ultima_fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_nivelActual) REFERENCES Niveles(id)
);

-- 4. Tabla de Intentos / Puntajes (Fusionada con los requerimientos del reto)
CREATE TABLE Intentos (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_usuario INTEGER NOT NULL,
    id_nivel INTEGER NOT NULL,
    id_reto INTEGER NOT NULL,          -- Requerido por su Endpoint 2 y 4
    score INTEGER NOT NULL,            -- El puntaje final
    tiempo_segundos INTEGER NOT NULL,  -- Requerido por el RF-12 y su Endpoint 2
    aciertos INTEGER DEFAULT 0,        -- Requerido para la analítica (RF-12)
    errores INTEGER DEFAULT 0,         -- Requerido para la analítica (RF-12)
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_nivel) REFERENCES Niveles(id)
);