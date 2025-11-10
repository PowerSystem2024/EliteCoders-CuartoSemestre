-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS db_todo_api;

-- Usar la base de datos
USE db_todo_api;

-- Crear la tabla de tareas
CREATE TABLE IF NOT EXISTS task (
  id bigint(20) NOT NULL,
  created_date datetime(6) NOT NULL,
  date date NOT NULL,
  enable bit(1) DEFAULT NULL,
  finished bit(1) NOT NULL,
  time time NOT NULL,
  title varchar(256) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Crear la tabla de secuencia
CREATE TABLE IF NOT EXISTS task_seq (
  next_val bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Inicializar la secuencia
INSERT INTO task_seq (next_val) VALUES (1) ON DUPLICATE KEY UPDATE next_val = next_val;