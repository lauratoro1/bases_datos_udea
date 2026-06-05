import requests
from pymongo import MongoClient

# Conexión MongoDB
cliente = MongoClient("mongodb://localhost:27017/")

# Base de datos
db = cliente["taller4_db"]

# Colección
coleccion = db["raw_data"]

# URL API
url = "https://thronesapi.com/api/v2/Characters"

# Solicitud GET
respuesta = requests.get(url)

# JSON RAW
datos = respuesta.json()

# Limpiar colección (opcional)
coleccion.delete_many({})

# Insertar datos
coleccion.insert_many(datos)

print("Ingesta completada correctamente")