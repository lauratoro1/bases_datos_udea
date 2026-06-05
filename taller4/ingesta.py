import requests
from pymongo import MongoClient

# Conexión MongoDB
cliente = MongoClient("mongodb://localhost:27017/")

# Base de datos
db = cliente["taller4_db"]

# Colección
coleccion = db["raw_data"]

# Limpiar colección
coleccion.delete_many({})

# URL API
url = "https://thronesapi.com/api/v2/Characters"

# Obtener datos
respuesta = requests.get(url)

datos = respuesta.json()

# Lista final
datos_finales = []

# Repetir registros hasta superar 100
while len(datos_finales) < 100:

    for personaje in datos:

        # Copia del documento
        nuevo_personaje = personaje.copy()

        # Eliminar _id si existe
        nuevo_personaje.pop("_id", None)

        datos_finales.append(nuevo_personaje)

        # Detener exactamente en 100
        if len(datos_finales) >= 100:
            break

# Insertar documentos
coleccion.insert_many(datos_finales)

print(f"Total registros insertados: {len(datos_finales)}")