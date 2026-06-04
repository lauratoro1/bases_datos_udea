# Taller 3 - Bases de Datos
#Laura María Toro Montoya

## Descripción

Este proyecto utiliza Python, SQLAlchemy y Faker para generar datos falsos y almacenarlos en una base de datos local SQLite.

El programa:

- Se conecta a una base de datos local.
- Crea automáticamente la tabla `personas_laura` si no existe.
- Genera 100000 registros falsos usando Faker.
- Inserta los datos en la base de datos utilizando SQLAlchemy.

La tabla contiene los siguientes atributos:

- id
- nombre
- correo
- ciudad
- pais
- profesion
- telefono
- empresa
- direccion

---

## Dependencias

Instalar las librerías necesarias con:

```bash
pip install sqlalchemy faker