Tema: aeropuerto
Tablas (3):
- pasajeros(id_pasajero PK, nombre, email, documento)
- vuelos(id_vuelo PK, origen, destino, aerolinea)
- reservas(id_reserva PK, id_pasajero FK->pasajeros.id_pasajero, id_vuelo FK->vuelos.id_vuelo,
           fecha_vuelo, clase {economica,ejecutiva,primera}, precio DECIMAL)
Notas: recaudo por aerolinea, rutas mas populares, precio promedio por clase, etc.