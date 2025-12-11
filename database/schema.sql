-- Tabla de usuarios administradores
CREATE TABLE IF NOT EXISTS administradores (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de torneos
CREATE TABLE IF NOT EXISTS torneos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'en_curso' CHECK (estado IN ('en_curso', 'finalizado')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    torneo_id INTEGER REFERENCES torneos(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    cantidad_cuadros INTEGER NOT NULL,
    personas_por_cuadro INTEGER NOT NULL,
    ganador VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de participantes
CREATE TABLE IF NOT EXISTS participantes (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    cuadro_numero INTEGER,
    posicion_en_cuadro INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de partidos (para los cuadros)
CREATE TABLE IF NOT EXISTS partidos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE CASCADE,
    cuadro_numero INTEGER NOT NULL,
    jugador1 VARCHAR(100),
    jugador2 VARCHAR(100),
    resultado VARCHAR(20),
    ganador VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de llaves
CREATE TABLE IF NOT EXISTS llaves (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE CASCADE,
    ronda INTEGER NOT NULL,
    posicion INTEGER NOT NULL,
    jugador VARCHAR(100),
    es_ganador BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuario administrador por defecto
INSERT INTO administradores (usuario, password) 
VALUES ('adminTM', 'adminTM2025') 
ON CONFLICT (usuario) DO NOTHING;