-- =========================================
-- CREACIÓN DE BASE DE DATOS
-- =========================================
CREATE DATABASE IF NOT EXISTS taller2;
USE taller2;

-- =========================================
-- TABLA: pasajeros
-- =========================================
CREATE TABLE pasajeros (
    id_pasajero INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    documento VARCHAR(50) NOT NULL UNIQUE
);

-- =========================================
-- TABLA: vuelos
-- =========================================
CREATE TABLE vuelos (
    id_vuelo INT PRIMARY KEY,
    origen VARCHAR(100) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    aerolinea VARCHAR(100) NOT NULL
);

-- =========================================
-- TABLA: reservas
-- =========================================
CREATE TABLE reservas (
    id_reserva INT PRIMARY KEY,
    id_pasajero INT NOT NULL,
    id_vuelo INT NOT NULL,
    fecha_vuelo DATE NOT NULL,
    clase ENUM('economica','ejecutiva','primera') NOT NULL,
    precio DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_pasajero) REFERENCES pasajeros(id_pasajero),
    FOREIGN KEY (id_vuelo) REFERENCES vuelos(id_vuelo),

    CHECK (precio > 0)
);

-- =========================================
-- BLOQUE A — CONOCIENDO LA BASE DE DATOS
-- =========================================

-- [A1]
-- Qué hace: Cuenta el número de registros en la tabla pasajeros.
-- Cómo funciona: Usa COUNT(*) para contar todas las filas de la tabla.

SELECT COUNT(*) AS total_pasajeros
FROM pasajeros;

-- [A1]
-- Qué hace: Cuenta el número de registros en la tabla vuelos.
-- Cómo funciona: COUNT(*) devuelve el total de filas.

SELECT COUNT(*) AS total_vuelos
FROM vuelos;

-- [A1]
-- Qué hace: Cuenta el número de registros en la tabla reservas.
-- Cómo funciona: COUNT(*) cuenta todos los registros almacenados.

SELECT COUNT(*) AS total_reservas
FROM reservas;


-- [A2]
-- Qué hace: Cuenta la cantidad de reservas agrupadas por mes.
-- Cómo funciona: Usa MONTH() para extraer el mes y GROUP BY para agrupar.

SELECT MONTH(fecha_vuelo) AS mes,
       COUNT(*) AS total_reservas
FROM reservas
GROUP BY MONTH(fecha_vuelo)
ORDER BY mes;


-- [A3]
-- Qué hace: Une reservas con pasajeros para mostrar información completa.
-- Cómo funciona: Usa INNER JOIN entre la FK (id_pasajero) y la PK.

SELECT r.id_reserva,
       p.nombre,
       r.fecha_vuelo,
       r.precio
FROM reservas r
INNER JOIN pasajeros p
ON r.id_pasajero = p.id_pasajero
LIMIT 10;


-- [A4]
-- Qué hace: Calcula el total recaudado por todas las reservas.
-- Cómo funciona: Usa SUM() sobre la columna precio.

SELECT SUM(precio) AS total_recaudado
FROM reservas;


-- [A5]
-- Qué hace: Lista las clases de vuelo sin repetir.
-- Cómo funciona: Usa DISTINCT para obtener valores únicos.

SELECT DISTINCT clase
FROM reservas;

-- =========================================
-- BLOQUE B — OPERADORES DE FILTRO
-- =========================================

-- [B1]
-- Qué hace: Cuenta las reservas en un rango de fechas específico.
-- Cómo funciona: Usa BETWEEN para filtrar fechas dentro del intervalo.

SELECT COUNT(*) AS total_reservas
FROM reservas
WHERE fecha_vuelo BETWEEN '2024-06-01' AND '2024-08-31';


-- [B2]
-- Qué hace: Filtra reservas por clases específicas (económica y primera).
-- Cómo funciona: Usa IN y LOWER para estandarizar valores en minúscula.

SELECT *
FROM reservas
WHERE LOWER(clase) IN ('economica','primera');


-- [B3]
-- Qué hace: Busca pasajeros cuyo nombre empieza por "an".
-- Cómo funciona: Usa LIKE con patrón y LOWER para evitar problemas de mayúsculas.

SELECT *
FROM pasajeros
WHERE LOWER(nombre) LIKE 'an%';


-- [B4]
-- Qué hace: Filtra pasajeros cuyos nombres contienen solo letras.
-- Cómo funciona: Usa REGEXP con una expresión regular.

SELECT *
FROM pasajeros
WHERE nombre REGEXP '^[A-Za-z ]+$';


-- [B5.1]
-- Qué hace: Filtra reservas económicas con precio mayor a 200.
-- Cómo funciona: Combina condiciones usando AND.

SELECT *
FROM reservas
WHERE clase = 'economica'
AND precio > 200;


-- [B5.2]
-- Qué hace: Filtra reservas que sean de clase primera o con precio alto.
-- Cómo funciona: Usa OR para incluir cualquiera de las condiciones.

SELECT *
FROM reservas
WHERE clase = 'primera'
OR precio > 1000;


-- [B6.1]
-- Qué hace: Establece algunos correos como NULL para simular datos faltantes.
-- Cómo funciona: Usa UPDATE para modificar registros específicos.

UPDATE pasajeros
SET email = NULL
WHERE id_pasajero IN (1,2,3);


-- [B6.2]
-- Qué hace: Muestra los pasajeros que tienen email NULL.
-- Cómo funciona: Usa IS NULL para filtrar valores faltantes.

SELECT *
FROM pasajeros
WHERE email IS NULL;

-- =========================================
-- BLOQUE C — NULOS, EXPRESIONES Y CASOS
-- =========================================

-- [C1]
-- Qué hace: Reemplaza los valores NULL en el email por "desconocido".
-- Cómo funciona: Usa COALESCE para mostrar un valor alternativo cuando hay NULL.

SELECT id_pasajero,
       nombre,
       COALESCE(email, 'desconocido') AS email_normalizado
FROM pasajeros;


-- [C2]
-- Qué hace: Clasifica las reservas según el precio en bajo, medio y alto.
-- Cómo funciona: Usa CASE WHEN con rangos de precio definidos.

SELECT id_reserva,
       precio,
       CASE
           WHEN precio < 200 THEN 'bajo'
           WHEN precio BETWEEN 200 AND 500 THEN 'medio'
           ELSE 'alto'
       END AS categoria_precio
FROM reservas;


-- [C3]
-- Qué hace: Muestra los vuelos que tienen al menos 5 reservas.
-- Cómo funciona: Agrupa por id_vuelo y usa HAVING para filtrar los grupos con COUNT >= 5.

SELECT id_vuelo,
       COUNT(*) AS total_reservas
FROM reservas
GROUP BY id_vuelo
HAVING COUNT(*) >= 5;

-- =========================================
-- BLOQUE D — SUBCONSULTAS Y CTE
-- =========================================

-- [D1]
-- Qué hace: Lista las reservas cuyo precio está por encima del promedio.
-- Cómo funciona: Usa una subconsulta para calcular el promedio y compara cada fila.

SELECT *
FROM reservas
WHERE precio > (
    SELECT AVG(precio)
    FROM reservas
);


-- [D2]
-- Qué hace: Repite D1 usando una CTE para calcular el promedio.
-- Cómo funciona: Define una CTE con el promedio y luego filtra usando ese valor.

WITH promedio AS (
    SELECT AVG(precio) AS prom_precio
    FROM reservas
)
SELECT r.*
FROM reservas r, promedio p
WHERE r.precio > p.prom_precio;


-- [D3]
-- Qué hace: Filtra las reservas de un mes específico (ej: julio).
-- Cómo funciona: Usa una CTE para aislar el mes y luego consulta sobre ella.

WITH reservas_julio AS (
    SELECT *
    FROM reservas
    WHERE MONTH(fecha_vuelo) = 7
)
SELECT *
FROM reservas_julio;


-- [D4]
-- Qué hace: Crea una vista con el detalle de reservas y datos del vuelo.
-- Cómo funciona: Define una VIEW y luego la consulta con SELECT.

CREATE VIEW vista_reservas AS
SELECT r.id_reserva,
       r.fecha_vuelo,
       r.precio,
       r.clase,
       v.aerolinea,
       v.origen,
       v.destino
FROM reservas r
INNER JOIN vuelos v
ON r.id_vuelo = v.id_vuelo;

-- Consulta a la vista
SELECT *
FROM vista_reservas;