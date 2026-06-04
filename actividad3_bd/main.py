from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from faker import Faker

Base = declarative_base()

# ==========================================
# TABLA
# ==========================================

class PersonasLaura(Base):

    __tablename__ = "personas_laura"

    id = Column(Integer, primary_key=True)

    nombre = Column(String(100))
    correo = Column(String(120))
    ciudad = Column(String(100))
    pais = Column(String(100))
    profesion = Column(String(100))
    telefono = Column(String(50))
    empresa = Column(String(100))
    direccion = Column(String(200))

# ==========================================
# MAIN
# ==========================================

def main():

    # Base de datos SQLite
    engine = create_engine("sqlite:///taller3.db")

    # Crear tabla
    Base.metadata.create_all(engine)

    # Sesión
    Session = sessionmaker(bind=engine)
    session = Session()

    fake = Faker()

    total_registros = 100000
    lote = 5000

    print("Generando registros...")

    # ======================================
    # INSERTAR POR BLOQUES
    # ======================================

    for inicio in range(0, total_registros, lote):

        datos = []

        for _ in range(lote):

            persona = PersonasLaura(

                nombre=fake.name(),
                correo=fake.email(),
                ciudad=fake.city(),
                pais=fake.country(),
                profesion=fake.job(),
                telefono=fake.phone_number(),
                empresa=fake.company(),
                direccion=fake.address()

            )

            datos.append(persona)

        session.bulk_save_objects(datos)

        session.commit()

        print(f"Insertados {inicio + lote} registros")

    # ======================================
    # VERIFICAR
    # ======================================

    cantidad = session.query(PersonasLaura).count()

    print(f"\nCantidad total en la tabla: {cantidad}")

# ==========================================
# EJECUCIÓN
# ==========================================

if __name__ == "__main__":
    main()