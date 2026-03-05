DROP TABLE IF EXISTS Progreso;
DROP TABLE IF EXISTS Intentos;
DROP TABLE IF EXISTS Niveles;
DROP TABLE IF EXISTS Usuario;

-- 1. Tabla de Usuarios
CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL, 
    rol TEXT NOT NULL CHECK (rol IN ('maestro', 'estudiante'))
);


CREATE TABLE Memoretos {
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_nivel INTEGER NOT NULL,
    nombre_memoreto TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    figuras INTEGER [] NOT NULL,
    intersecciones INTEGER [] NOT NULL,
    FOREIGN KEY (id_nivel) REFERENCES Niveles(id)
}

-- 3. Tabla de Session / Puntajes (Fusionada con los requerimientos del reto)
CREATE TABLE Session (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_usuario INTEGER NOT NULL,
    id_reto INTEGER NOT NULL,          -- Requerido por su Endpoint 2 y 4
    score INTEGER NOT NULL,            -- El puntaje final
    tiempo_segundos INTEGER NOT NULL,  -- Requerido por el RF-12 y su Endpoint 2
    aciertos INTEGER DEFAULT 0,        -- Requerido para la analítica (RF-12)
    errores INTEGER DEFAULT 0,         -- Requerido para la analítica (RF-12)
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_nivel) REFERENCES Niveles(id)
);