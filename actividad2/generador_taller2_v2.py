# -*- coding: utf-8 -*-
"""
Generador aleatorio para Taller SQL (3 tablas, múltiples temáticas).
Uso:
  python generador_taller2_v2.py ecommerce --n 120 --out ./datos --seed 42
Temas: ecommerce, biblioteca, clinica, universidad, eventos, gimnasio,
       transporte, streaming, restaurante
Salida: 3 CSV + README.txt con el esquema y claves foráneas.
"""
import os, csv, argparse, random
from datetime import datetime, timedelta
from pathlib import Path

# ── Constantes ────────────────────────────────────────────────────────────────
_NOMBRES = [
    "Ana","Luis","Carlos","Marta","Pedro","Lucia","Sofia","Jorge",
    "Camila","Andres","Diana","Juan","Laura","Felipe","Valentina",
    "Miguel","Sara","Sebastian","Paula","Nicolas",
]
_APELLIDOS = [
    "Gomez","Perez","Rodriguez","Martinez","Garcia","Hernandez","Diaz",
    "Lopez","Torres","Castro","Ramos","Vargas","Suarez","Morales",
    "Romero","Navarro","Cruz","Molina","Rojas",
]

# ── Utilidades ────────────────────────────────────────────────────────────────
def rand_name():
    return f"{random.choice(_NOMBRES)} {random.choice(_APELLIDOS)}"

def rand_email(nombre, i, domain="example.com"):
    return f"{nombre.lower().replace(' ', '.')}.{i}@{domain}"

def _rand_date(base: datetime, days: int) -> str:
    """Fecha aleatoria entre base y base+days (inclusive)."""
    return (base + timedelta(days=random.randint(0, days))).date().isoformat()

def write_csv(path, rows, header):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def ensure(cond, msg):
    if not cond:
        raise ValueError(msg)

def _parse_date(s):
    if s in (None, "", "None"):
        return None
    return datetime.fromisoformat(str(s))

# ── Runner genérico ───────────────────────────────────────────────────────────
def _run(n, outdir, theme_name, build_fn, validate_fn, csv_specs, schema):
    """Genera con reintentos, valida y escribe archivos."""
    for _ in range(10):
        tables = build_fn(n)
        try:
            validate_fn(*tables)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"{theme_name}: no se pudo generar dataset válido tras 10 intentos")
    for (filename, header), rows in zip(csv_specs, tables):
        write_csv(os.path.join(outdir, filename), rows, header)
    Path(outdir, "README.txt").write_text(schema, encoding="utf-8")

# ── Validadores ───────────────────────────────────────────────────────────────
def validate_ecommerce(clientes, pedidos, pagos):
    ids_c = {c[0] for c in clientes}
    ensure(len(ids_c) == len(clientes), "Duplicate id_cliente")
    pedidos_by_id = {p[0]: p for p in pedidos}
    for p in pedidos:
        ensure(p[1] in ids_c, f"Pedido {p[0]} cliente {p[1]} missing")
        ensure(float(p[3]) >= 0.0, f"Pedido {p[0]} total_estimado < 0")
    sum_pagos = {}
    for pa in pagos:
        ensure(pa[1] in pedidos_by_id, f"Pago {pa[0]} pedido {pa[1]} missing")
        ensure(float(pa[3]) > 0.0, f"Pago {pa[0]} monto <= 0")
        ensure(pa[4] in {"tarjeta","efectivo","transferencia"}, f"Pago {pa[0]} metodo invalid")
        sum_pagos[pa[1]] = sum_pagos.get(pa[1], 0.0) + float(pa[3])
    for pid, p in pedidos_by_id.items():
        if pid in sum_pagos:
            total = float(p[3])
            diff = abs(sum_pagos[pid] - total)
            tol = max(1.5, total * 0.07)
            ensure(diff <= tol, f"Sum pagos pedido {pid} diff={diff:.2f} > tol={tol:.2f}")

def validate_biblioteca(libros, socios, prestamos):
    ids_l = {l[0] for l in libros}
    ids_s = {s[0] for s in socios}
    ensure(len(ids_l) == len(libros), "Duplicate id_libro")
    ensure(len(ids_s) == len(socios), "Duplicate id_socio")
    for l in libros:
        ensure(int(l[4]) >= 50, f"Libro {l[0]} paginas < 50")
    for pr in prestamos:
        ensure(pr[1] in ids_s, f"Prestamo {pr[0]} socio {pr[1]} missing")
        ensure(pr[2] in ids_l, f"Prestamo {pr[0]} libro {pr[2]} missing")
        fp = _parse_date(pr[3])
        fd = _parse_date(pr[4])
        ensure(fp is not None, f"Prestamo {pr[0]} fecha_prestamo missing")
        if fd is not None:
            ensure(fd >= fp, f"Prestamo {pr[0]} devolucion before prestamo")

def validate_clinica(medicos, pacientes, citas):
    ids_m = {m[0] for m in medicos}
    ids_p = {p[0] for p in pacientes}
    ensure(len(ids_m) == len(medicos), "Duplicate id_medico")
    ensure(len(ids_p) == len(pacientes), "Duplicate id_paciente")
    for c in citas:
        ensure(c[1] in ids_p, f"Cita {c[0]} paciente {c[1]} missing")
        ensure(c[2] in ids_m, f"Cita {c[0]} medico {c[2]} missing")
        ensure(c[4] in {"programada","atendida","cancelada"}, f"Cita {c[0]} estado invalid")
        ensure(float(c[5]) > 0.0, f"Cita {c[0]} costo_consulta <= 0")

def validate_universidad(estudiantes, cursos, matriculas):
    ids_e = {e[0] for e in estudiantes}
    ids_c = {c[0] for c in cursos}
    ensure(len(ids_e) == len(estudiantes), "Duplicate id_estudiante")
    ensure(len(ids_c) == len(cursos), "Duplicate id_curso")
    semestres = {"2024-1","2024-2","2025-1"}
    for m in matriculas:
        ensure(m[1] in ids_e, f"Matricula {m[0]} estudiante {m[1]} missing")
        ensure(m[2] in ids_c, f"Matricula {m[0]} curso {m[2]} missing")
        ensure(m[3] in semestres, f"Matricula {m[0]} semestre invalid: {m[3]}")
        ensure(m[4] in {"inscrito","aprobado","reprobado"}, f"Matricula {m[0]} estado invalid")
        ensure(_parse_date(m[5]) is not None, f"Matricula {m[0]} fecha_matricula missing")

def validate_eventos(eventos, asistentes, tickets):
    ids_e = {e[0] for e in eventos}
    ids_a = {a[0] for a in asistentes}
    ensure(len(ids_e) == len(eventos), "Duplicate id_evento")
    ensure(len(ids_a) == len(asistentes), "Duplicate id_asistente")
    for t in tickets:
        ensure(t[1] in ids_e, f"Ticket {t[0]} evento {t[1]} missing")
        ensure(t[2] in ids_a, f"Ticket {t[0]} asistente {t[2]} missing")
        ensure(float(t[3]) >= 0.0, f"Ticket {t[0]} precio < 0")
        ensure(t[4] in {"pagado","pendiente","cancelado"}, f"Ticket {t[0]} estado invalid")

def validate_gimnasio(miembros, clases, asistencias):
    ids_m = {m[0] for m in miembros}
    ids_c = {c[0] for c in clases}
    ensure(len(ids_m) == len(miembros), "Duplicate id_miembro")
    ensure(len(ids_c) == len(clases), "Duplicate id_clase")
    for a in asistencias:
        ensure(a[1] in ids_m, f"Asistencia {a[0]} miembro {a[1]} missing")
        ensure(a[2] in ids_c, f"Asistencia {a[0]} clase {a[2]} missing")
        ensure(a[4] in {"asistio","no_asistio","cancelada"}, f"Asistencia {a[0]} estado invalid")

def validate_transporte(usuarios, recargas, viajes):
    ids_u = {u[0] for u in usuarios}
    ensure(len(ids_u) == len(usuarios), "Duplicate id_usuario")
    for r in recargas:
        ensure(r[1] in ids_u, f"Recarga {r[0]} usuario {r[1]} missing")
        ensure(_parse_date(r[2]) is not None, f"Recarga {r[0]} fecha missing")
        ensure(float(r[3]) >= 0.0, f"Recarga {r[0]} monto < 0")
        ensure(r[4] in {"tarjeta","efectivo","app"}, f"Recarga {r[0]} metodo invalid")
    for v in viajes:
        ensure(v[1] in ids_u, f"Viaje {v[0]} usuario {v[1]} missing")
        ensure(_parse_date(v[2]) is not None, f"Viaje {v[0]} fecha missing")
        ensure(v[3] in {"A","B","C","D","E"}, f"Viaje {v[0]} ruta invalid")
        ensure(float(v[4]) >= 0.0, f"Viaje {v[0]} tarifa < 0")

def validate_streaming(usuarios, contenidos, visualizaciones):
    ids_u = {u[0] for u in usuarios}
    cont_by_id = {c[0]: c for c in contenidos}
    ensure(len(ids_u) == len(usuarios), "Duplicate id_usuario")
    ensure(len(cont_by_id) == len(contenidos), "Duplicate id_contenido")
    for v in visualizaciones:
        ensure(v[1] in ids_u, f"Visualizacion {v[0]} usuario {v[1]} missing")
        ensure(v[2] in cont_by_id, f"Visualizacion {v[0]} contenido {v[2]} missing")
        ensure(_parse_date(v[3]) is not None, f"Visualizacion {v[0]} fecha missing")
        dur, mins = int(cont_by_id[v[2]][3]), int(v[4])
        ensure(1 <= mins <= dur, f"Visualizacion {v[0]} minutos={mins} > dur={dur}")

def validate_restaurante(clientes, reservas, cuentas):
    ids_c = {c[0] for c in clientes}
    ensure(len(ids_c) == len(clientes), "Duplicate id_cliente")
    res_by_id = {r[0]: r for r in reservas}
    for r in reservas:
        ensure(r[1] in ids_c, f"Reserva {r[0]} cliente {r[1]} missing")
        ensure(_parse_date(r[2]) is not None, f"Reserva {r[0]} fecha missing")
        ensure(1 <= int(r[3]) <= 6, f"Reserva {r[0]} personas={r[3]} out of range")
        ensure(r[4] in {"confirmada","no_show","cancelada"}, f"Reserva {r[0]} estado invalid")
    for cta in cuentas:
        ensure(cta[1] in res_by_id, f"Cuenta {cta[0]} reserva {cta[1]} missing")
        ensure(float(cta[2]) > 0.0, f"Cuenta {cta[0]} total <= 0")
        ensure(float(cta[3]) >= 0.0, f"Cuenta {cta[0]} propina < 0")
        ensure(cta[4] in {"efectivo","tarjeta"}, f"Cuenta {cta[0]} metodo invalid")
        ensure(res_by_id[cta[1]][4] == "confirmada", f"Cuenta {cta[0]} reserva no confirmada")

def validate_hotel(huespedes, habitaciones, reservas):
    ids_h = {h[0] for h in huespedes}
    ids_hab = {h[0] for h in habitaciones}
    ensure(len(ids_h) == len(huespedes), "Duplicate id_huesped")
    ensure(len(ids_hab) == len(habitaciones), "Duplicate id_habitacion")
    for h in habitaciones:
        ensure(h[2] in {"simple","doble","suite"}, f"Habitacion {h[0]} tipo invalid")
        ensure(float(h[3]) > 0.0, f"Habitacion {h[0]} precio_noche <= 0")
    for r in reservas:
        ensure(r[1] in ids_h,   f"Reserva {r[0]} huesped {r[1]} missing")
        ensure(r[2] in ids_hab, f"Reserva {r[0]} habitacion {r[2]} missing")
        fi, fo = _parse_date(r[3]), _parse_date(r[4])
        ensure(fi is not None, f"Reserva {r[0]} fecha_checkin missing")
        ensure(fo is not None, f"Reserva {r[0]} fecha_checkout missing")
        ensure(fo > fi, f"Reserva {r[0]} checkout <= checkin")
        ensure(r[5] in {"confirmada","cancelada","completada"}, f"Reserva {r[0]} estado invalid")
        ensure(float(r[6]) > 0.0, f"Reserva {r[0]} total <= 0")

def validate_farmacia(clientes, medicamentos, ventas):
    ids_c = {c[0] for c in clientes}
    ids_m = {m[0] for m in medicamentos}
    ensure(len(ids_c) == len(clientes),     "Duplicate id_cliente")
    ensure(len(ids_m) == len(medicamentos), "Duplicate id_medicamento")
    cats = {"analgesico","antibiotico","vitamina","antiinflamatorio","antihistaminico"}
    for m in medicamentos:
        ensure(m[2] in cats,         f"Medicamento {m[0]} categoria invalid")
        ensure(float(m[3]) > 0.0,   f"Medicamento {m[0]} precio_unitario <= 0")
    for v in ventas:
        ensure(v[1] in ids_c, f"Venta {v[0]} cliente {v[1]} missing")
        ensure(v[2] in ids_m, f"Venta {v[0]} medicamento {v[2]} missing")
        ensure(_parse_date(v[3]) is not None, f"Venta {v[0]} fecha missing")
        ensure(int(v[4]) >= 1,       f"Venta {v[0]} cantidad < 1")
        ensure(float(v[5]) > 0.0,   f"Venta {v[0]} total <= 0")

def validate_banco(clientes, cuentas, transacciones):
    ids_c   = {c[0] for c in clientes}
    ids_cta = {c[0] for c in cuentas}
    ensure(len(ids_c)   == len(clientes),  "Duplicate id_cliente")
    ensure(len(ids_cta) == len(cuentas),   "Duplicate id_cuenta")
    for c in cuentas:
        ensure(c[1] in ids_c, f"Cuenta {c[0]} cliente {c[1]} missing")
        ensure(c[2] in {"corriente","ahorros"}, f"Cuenta {c[0]} tipo_cuenta invalid")
        ensure(float(c[3]) >= 0.0, f"Cuenta {c[0]} saldo < 0")
    for t in transacciones:
        ensure(t[1] in ids_cta, f"Transaccion {t[0]} cuenta {t[1]} missing")
        ensure(_parse_date(t[2]) is not None, f"Transaccion {t[0]} fecha missing")
        ensure(t[3] in {"deposito","retiro","transferencia"}, f"Transaccion {t[0]} tipo invalid")
        ensure(float(t[4]) > 0.0, f"Transaccion {t[0]} monto <= 0")

def validate_cine(peliculas, clientes, entradas):
    ids_p = {p[0] for p in peliculas}
    ids_c = {c[0] for c in clientes}
    ensure(len(ids_p) == len(peliculas), "Duplicate id_pelicula")
    ensure(len(ids_c) == len(clientes),  "Duplicate id_cliente")
    for p in peliculas:
        ensure(p[2] in {"accion","comedia","drama","terror","animacion"}, f"Pelicula {p[0]} genero invalid")
        ensure(int(p[3]) > 0, f"Pelicula {p[0]} duracion_min <= 0")
    for e in entradas:
        ensure(e[1] in ids_p, f"Entrada {e[0]} pelicula {e[1]} missing")
        ensure(e[2] in ids_c, f"Entrada {e[0]} cliente {e[2]} missing")
        ensure(_parse_date(e[3]) is not None, f"Entrada {e[0]} fecha_funcion missing")
        ensure(e[4] in {"A","B","C","D"}, f"Entrada {e[0]} sala invalid")
        ensure(float(e[5]) > 0.0, f"Entrada {e[0]} precio <= 0")

def validate_veterinaria(duenos, mascotas, consultas):
    ids_d = {d[0] for d in duenos}
    ids_m = {m[0] for m in mascotas}
    ensure(len(ids_d) == len(duenos),   "Duplicate id_dueno")
    ensure(len(ids_m) == len(mascotas), "Duplicate id_mascota")
    for m in mascotas:
        ensure(m[1] in ids_d, f"Mascota {m[0]} dueno {m[1]} missing")
        ensure(m[3] in {"perro","gato","ave","conejo","reptil"}, f"Mascota {m[0]} especie invalid")
        ensure(int(m[4]) >= 0, f"Mascota {m[0]} edad_anios < 0")
    for c in consultas:
        ensure(c[1] in ids_m, f"Consulta {c[0]} mascota {c[1]} missing")
        ensure(_parse_date(c[2]) is not None, f"Consulta {c[0]} fecha_consulta missing")
        ensure(float(c[4]) > 0.0, f"Consulta {c[0]} costo <= 0")

def validate_supermercado(clientes, productos, compras):
    ids_c = {c[0] for c in clientes}
    ids_p = {p[0] for p in productos}
    ensure(len(ids_c) == len(clientes),  "Duplicate id_cliente")
    ensure(len(ids_p) == len(productos), "Duplicate id_producto")
    cats = {"lacteos","carnes","bebidas","frutas","limpieza","panaderia"}
    for p in productos:
        ensure(p[2] in cats,       f"Producto {p[0]} categoria invalid")
        ensure(float(p[3]) > 0.0, f"Producto {p[0]} precio_unitario <= 0")
    for c in compras:
        ensure(c[1] in ids_c, f"Compra {c[0]} cliente {c[1]} missing")
        ensure(c[2] in ids_p, f"Compra {c[0]} producto {c[2]} missing")
        ensure(_parse_date(c[3]) is not None, f"Compra {c[0]} fecha missing")
        ensure(int(c[4]) >= 1,     f"Compra {c[0]} cantidad < 1")
        ensure(float(c[5]) > 0.0, f"Compra {c[0]} total <= 0")

def validate_aeropuerto(pasajeros, vuelos, reservas):
    ids_p = {p[0] for p in pasajeros}
    ids_v = {v[0] for v in vuelos}
    ensure(len(ids_p) == len(pasajeros), "Duplicate id_pasajero")
    ensure(len(ids_v) == len(vuelos),    "Duplicate id_vuelo")
    for r in reservas:
        ensure(r[1] in ids_p, f"Reserva {r[0]} pasajero {r[1]} missing")
        ensure(r[2] in ids_v, f"Reserva {r[0]} vuelo {r[2]} missing")
        ensure(_parse_date(r[3]) is not None, f"Reserva {r[0]} fecha_vuelo missing")
        ensure(r[4] in {"economica","ejecutiva","primera"}, f"Reserva {r[0]} clase invalid")
        ensure(float(r[5]) > 0.0, f"Reserva {r[0]} precio <= 0")

# ── Generadores por tema ──────────────────────────────────────────────────────
def gen_ecommerce(n, outdir):
    hoy = datetime(2024, 3, 1)
    def build(n):
        clientes = []
        for i in range(1, n+1):
            nombre = rand_name()
            clientes.append([i, nombre, rand_email(nombre, i), _rand_date(hoy - timedelta(days=400), 399)])
        pedidos, pagos = [], []
        for pid in range(1, int(1.8*n)+1):
            id_c = random.randint(1, n)
            fecha = _rand_date(hoy, 180)
            total = round(random.uniform(10, 800), 2)
            pedidos.append([pid, id_c, fecha, total])
            if random.random() < 0.85:
                numpagos = 2 if random.random() < 0.2 else 1
                resto = total
                for j in range(numpagos):
                    if j == numpagos - 1:
                        monto = max(1.0, round(resto * random.uniform(0.95, 1.05), 2))
                    else:
                        monto = round(resto * random.uniform(0.3, 0.7), 2)
                        resto -= monto
                    pagos.append([len(pagos)+1, pid, fecha, monto,
                                  random.choice(["tarjeta","efectivo","transferencia"])])
        return clientes, pedidos, pagos
    _run(n, outdir, "ecommerce", build, validate_ecommerce,
         [("clientes.csv", ["id_cliente","nombre","email","fecha_alta"]),
          ("pedidos.csv",  ["id_pedido","id_cliente","fecha_pedido","total_estimado"]),
          ("pagos.csv",    ["id_pago","id_pedido","fecha_pago","monto","metodo"])],
         "Tema: ecommerce\nTablas (3):\n"
         "- clientes(id_cliente PK, nombre, email, fecha_alta)\n"
         "- pedidos(id_pedido PK, id_cliente FK->clientes.id_cliente, fecha_pedido, total_estimado)\n"
         "- pagos(id_pago PK, id_pedido FK->pedidos.id_pedido, fecha_pago, monto,"
         " metodo {tarjeta,efectivo,transferencia})\n"
         "Notas: ~15% de pedidos no tienen pago (LEFT JOIN para detectarlos).")

def gen_biblioteca(n, outdir):
    hoy = datetime(2024, 3, 1)
    def build(n):
        libros = [[i, f"Libro {i}", rand_name(), random.randint(1990, 2024), random.randint(80, 800)]
                  for i in range(1, n+1)]
        socios = []
        for i in range(1, int(n*0.8)+1):
            nombre = rand_name()
            socios.append([i, nombre, rand_email(nombre, i, "biblio.com"),
                           _rand_date(hoy - timedelta(days=800), 799)])
        prestamos = []
        for pid in range(1, int(1.5*n)+1):
            fp = _rand_date(hoy, 120)
            fp_dt = datetime.fromisoformat(fp)
            fd = None if random.random() < 0.4 else _rand_date(fp_dt + timedelta(days=10), 170)
            prestamos.append([pid, random.randint(1, len(socios)), random.randint(1, n), fp, fd])
        return libros, socios, prestamos
    _run(n, outdir, "biblioteca", build, validate_biblioteca,
         [("libros.csv",    ["id_libro","titulo","autor","anio","paginas"]),
          ("socios.csv",    ["id_socio","nombre","email","fecha_alta"]),
          ("prestamos.csv", ["id_prestamo","id_socio","id_libro","fecha_prestamo","fecha_devolucion"])],
         "Tema: biblioteca\nTablas (3):\n"
         "- libros(id_libro PK, titulo, autor, anio, paginas INT)\n"
         "- socios(id_socio PK, nombre, email, fecha_alta)\n"
         "- prestamos(id_prestamo PK, id_socio FK->socios.id_socio, id_libro FK->libros.id_libro,\n"
         "            fecha_prestamo, fecha_devolucion NULL ~40%)\n"
         "Notas: hay prestamos activos (sin devolucion). LEFT JOIN/IS NULL para detectarlos.")

def gen_clinica(n, outdir):
    hoy          = datetime(2024, 3, 1)
    especialidades = ["general","pediatria","dermatologia","cardiologia","odontologia","oftalmologia"]
    def build(n):
        medicos   = [[i, rand_name(), random.choice(especialidades)]
                     for i in range(1, max(5, int(n*0.1))+1)]
        pacientes = [[i, rand_name(), f"DOC{i:06d}"] for i in range(1, n+1)]
        citas     = [
            [cid, random.randint(1, n), random.randint(1, len(medicos)),
             _rand_date(hoy, 90),
             random.choices(["programada","atendida","cancelada"], weights=[0.25,0.65,0.10])[0],
             round(random.uniform(50.0, 300.0), 2)]
            for cid in range(1, int(1.2*n)+1)
        ]
        return medicos, pacientes, citas
    _run(n, outdir, "clinica", build, validate_clinica,
         [("medicos.csv",   ["id_medico","nombre","especialidad"]),
          ("pacientes.csv", ["id_paciente","nombre","documento"]),
          ("citas.csv",     ["id_cita","id_paciente","id_medico","fecha_cita","estado","costo_consulta"])],
         "Tema: clinica\nTablas (3):\n"
         "- medicos(id_medico PK, nombre, especialidad)\n"
         "- pacientes(id_paciente PK, nombre, documento)\n"
         "- citas(id_cita PK, id_paciente FK->pacientes.id_paciente, id_medico FK->medicos.id_medico,\n"
         "        fecha_cita, estado {programada,atendida,cancelada}, costo_consulta DECIMAL)\n"
         "Notas: atencion por especialidad, cancelaciones por mes, costo total por medico, etc.")

def gen_universidad(n, outdir):
    carreras      = ["sistemas","industrial","medicina","derecho","economia","matematicas"]
    nombres_curso = ["Algebra","Calculo","Programacion","Bases_de_datos",
                     "Probabilidad","Microeconomia","Fisica"]
    # (base_date, días máx dentro del semestre)
    semestre_rango = {
        "2024-1": (datetime(2024, 1, 15), 167),
        "2024-2": (datetime(2024, 7, 15), 153),
        "2025-1": (datetime(2025, 1, 15), 166),
    }
    def build(n):
        estudiantes = [[i, rand_name(), random.choice(carreras)] for i in range(1, n+1)]
        cursos      = [[i, random.choice(nombres_curso)+f"_{i}", random.choice([2,3,4])]
                       for i in range(1, max(6, int(n*0.08))+1)]
        matriculas  = []
        for mid in range(1, int(1.4*n)+1):
            semestre       = random.choice(["2024-1","2024-2","2025-1"])
            base, dias     = semestre_rango[semestre]
            matriculas.append([
                mid, random.randint(1, n), random.randint(1, len(cursos)),
                semestre, random.choice(["inscrito","aprobado","reprobado"]),
                _rand_date(base, dias),
            ])
        return estudiantes, cursos, matriculas
    _run(n, outdir, "universidad", build, validate_universidad,
         [("estudiantes.csv", ["id_estudiante","nombre","carrera"]),
          ("cursos.csv",      ["id_curso","nombre_curso","creditos"]),
          ("matriculas.csv",  ["id_matricula","id_estudiante","id_curso",
                                "semestre","estado","fecha_matricula"])],
         "Tema: universidad\nTablas (3):\n"
         "- estudiantes(id_estudiante PK, nombre, carrera)\n"
         "- cursos(id_curso PK, nombre_curso, creditos)\n"
         "- matriculas(id_matricula PK, id_estudiante FK->estudiantes.id_estudiante,"
         " id_curso FK->cursos.id_curso,\n"
         "             semestre, estado {inscrito,aprobado,reprobado}, fecha_matricula DATE)\n"
         "Notas: JOIN para ver carga por carrera, tasas de aprobacion por curso,"
         " conteo por mes con MONTH(fecha_matricula).")

def gen_eventos(n, outdir):
    hoy   = datetime(2024, 6, 1)
    sedes = ["auditorio_norte","plaza_central","teatro_arte","coliseo_universitario"]
    def build(n):
        eventos    = [[i, f"Evento_{i}", _rand_date(hoy, 90), random.choice(sedes)]
                      for i in range(1, max(6, int(n*0.08))+1)]
        asistentes = []
        for i in range(1, n+1):
            nombre = rand_name()
            asistentes.append([i, nombre, f"{nombre.lower().replace(' ','.')}.{i}@mail.com"])
        tickets = [
            [tid, random.randint(1, len(eventos)), random.randint(1, n),
             round(random.uniform(10, 120), 2),
             random.choices(["pagado","pendiente","cancelado"], weights=[0.7,0.2,0.1])[0]]
            for tid in range(1, int(1.1*n)+1)
        ]
        return eventos, asistentes, tickets
    _run(n, outdir, "eventos", build, validate_eventos,
         [("eventos.csv",    ["id_evento","nombre_evento","fecha_evento","sede"]),
          ("asistentes.csv", ["id_asistente","nombre","email"]),
          ("tickets.csv",    ["id_ticket","id_evento","id_asistente","precio","estado"])],
         "Tema: eventos\nTablas (3):\n"
         "- eventos(id_evento PK, nombre_evento, fecha_evento, sede)\n"
         "- asistentes(id_asistente PK, nombre, email)\n"
         "- tickets(id_ticket PK, id_evento FK->eventos.id_evento,"
         " id_asistente FK->asistentes.id_asistente,\n"
         "          precio, estado {pagado,pendiente,cancelado})\n"
         "Notas: LEFT JOIN para pendientes/cancelados por evento, top sedes por recaudo, etc.")

def gen_gimnasio(n, outdir):
    tipos = ["yoga","spinning","hiit","fuerza","pilates"]
    hoy   = datetime(2024, 4, 1)
    def build(n):
        miembros    = [[i, rand_name(), f"+57{random.randint(3000000000, 3999999999)}"]
                       for i in range(1, n+1)]
        clases      = [[i, random.choice(tipos), random.randint(10, 40)]
                       for i in range(1, max(6, int(n*0.06))+1)]
        asistencias = [
            [aid, random.randint(1, n), random.randint(1, len(clases)),
             _rand_date(hoy, 120),
             random.choices(["asistio","no_asistio","cancelada"], weights=[0.7,0.2,0.1])[0]]
            for aid in range(1, int(1.2*n)+1)
        ]
        return miembros, clases, asistencias
    _run(n, outdir, "gimnasio", build, validate_gimnasio,
         [("miembros.csv",    ["id_miembro","nombre","telefono"]),
          ("clases.csv",      ["id_clase","tipo","cupo"]),
          ("asistencias.csv", ["id_asistencia","id_miembro","id_clase","fecha","estado"])],
         "Tema: gimnasio\nTablas (3):\n"
         "- miembros(id_miembro PK, nombre, telefono)\n"
         "- clases(id_clase PK, tipo, cupo)\n"
         "- asistencias(id_asistencia PK, id_miembro FK->miembros.id_miembro,"
         " id_clase FK->clases.id_clase,\n"
         "              fecha, estado {asistio,no_asistio,cancelada})\n"
         "Notas: TOP clases por asistencia, tasas por estado, etc.")

def gen_transporte(n, outdir):
    hoy = datetime(2024, 5, 1)
    def build(n):
        usuarios = [[i, rand_name(), f"C{i:07d}"] for i in range(1, n+1)]
        recargas = [
            [rid, random.randint(1, n), _rand_date(hoy, 150),
             round(random.uniform(5, 50), 2), random.choice(["tarjeta","efectivo","app"])]
            for rid in range(1, int(1.2*n)+1)
        ]
        viajes = [
            [vid, random.randint(1, n), _rand_date(hoy, 150),
             random.choice(["A","B","C","D","E"]), round(random.uniform(1.5, 6.0), 2)]
            for vid in range(1, int(1.5*n)+1)
        ]
        return usuarios, recargas, viajes
    _run(n, outdir, "transporte", build, validate_transporte,
         [("usuarios.csv", ["id_usuario","nombre","documento"]),
          ("recargas.csv", ["id_recarga","id_usuario","fecha","monto","metodo"]),
          ("viajes.csv",   ["id_viaje","id_usuario","fecha","ruta","tarifa"])],
         "Tema: transporte\nTablas (3):\n"
         "- usuarios(id_usuario PK, nombre, documento)\n"
         "- recargas(id_recarga PK, id_usuario FK->usuarios.id_usuario, fecha, monto,"
         " metodo {tarjeta,efectivo,app})\n"
         "- viajes(id_viaje PK, id_usuario FK->usuarios.id_usuario, fecha, ruta, tarifa)\n"
         "Notas: gastos por ruta, saldo teorico recargas - viajes, usuarios sin recargas, etc.")

def gen_streaming(n, outdir):
    generos = ["drama","accion","comedia","documental","scifi","terror"]
    hoy     = datetime(2024, 2, 1)
    def build(n):
        usuarios   = [[i, rand_name(), f"u{i:05d}@stream.tv"] for i in range(1, n+1)]
        contenidos = [[i, f"Titulo_{i}", random.choice(generos), random.randint(30, 180)]
                      for i in range(1, max(8, int(n*0.08))+1)]
        cont_dur   = {c[0]: c[3] for c in contenidos}
        visualizaciones = []
        for vid in range(1, int(2.0*n)+1):
            id_u = random.randint(1, n)
            id_c = random.randint(1, len(contenidos))
            fecha = _rand_date(hoy, 180)
            visualizaciones.append([vid, id_u, id_c, fecha, random.randint(1, cont_dur[id_c])])
        return usuarios, contenidos, visualizaciones
    _run(n, outdir, "streaming", build, validate_streaming,
         [("usuarios.csv",        ["id_usuario","nombre","email"]),
          ("contenidos.csv",      ["id_contenido","titulo","genero","duracion_min"]),
          ("visualizaciones.csv", ["id_visualizacion","id_usuario","id_contenido",
                                    "fecha","minutos_vistos"])],
         "Tema: streaming\nTablas (3):\n"
         "- usuarios(id_usuario PK, nombre, email)\n"
         "- contenidos(id_contenido PK, titulo, genero, duracion_min)\n"
         "- visualizaciones(id_visualizacion PK, id_usuario FK->usuarios.id_usuario,"
         " id_contenido FK->contenidos.id_contenido,\n"
         "                  fecha, minutos_vistos)\n"
         "Notas: TOP generos por tiempo visto, usuarios sin actividad, etc.")

def gen_restaurante(n, outdir):
    hoy = datetime(2024, 7, 1)
    def build(n):
        clientes = []
        for i in range(1, n+1):
            nombre = rand_name()
            clientes.append([i, nombre, rand_email(nombre, i, "resto.com")])
        reservas, cuentas = [], []
        for rid in range(1, int(1.1*n)+1):
            estado = random.choices(["confirmada","no_show","cancelada"], weights=[0.7,0.15,0.15])[0]
            reservas.append([rid, random.randint(1, n), _rand_date(hoy, 90),
                             random.randint(1, 6), estado])
            if estado == "confirmada" and random.random() < 0.9:
                total = round(random.uniform(15, 200), 2)
                cuentas.append([len(cuentas)+1, rid, total,
                                round(total * random.uniform(0.05, 0.15), 2),
                                random.choice(["efectivo","tarjeta"])])
        return clientes, reservas, cuentas
    _run(n, outdir, "restaurante", build, validate_restaurante,
         [("clientes.csv", ["id_cliente","nombre","email"]),
          ("reservas.csv", ["id_reserva","id_cliente","fecha","personas","estado"]),
          ("cuentas.csv",  ["id_cuenta","id_reserva","total","propina","metodo_pago"])],
         "Tema: restaurante\nTablas (3):\n"
         "- clientes(id_cliente PK, nombre, email)\n"
         "- reservas(id_reserva PK, id_cliente FK->clientes.id_cliente, fecha, personas,"
         " estado {confirmada,no_show,cancelada})\n"
         "- cuentas(id_cuenta PK, id_reserva FK->reservas.id_reserva, total, propina,"
         " metodo_pago {efectivo,tarjeta})\n"
         "Notas: no_show por mes, ticket promedio, clientes sin consumo, etc.")

def gen_hotel(n, outdir):
    hoy   = datetime(2024, 4, 1)
    tipos = ["simple","doble","suite"]
    precios = {"simple": (60.0, 120.0), "doble": (100.0, 200.0), "suite": (200.0, 450.0)}
    def build(n):
        huespedes = []
        for i in range(1, n+1):
            nombre = rand_name()
            huespedes.append([i, nombre, rand_email(nombre, i, "hotel.com"), f"ID{i:07d}"])
        habitaciones = []
        for i in range(1, max(10, int(n*0.1))+1):
            tipo = random.choice(tipos)
            lo, hi = precios[tipo]
            habitaciones.append([i, f"{100 + i}", tipo, round(random.uniform(lo, hi), 2)])
        reservas = []
        for rid in range(1, int(1.2*n)+1):
            id_h   = random.randint(1, n)
            id_hab = random.randint(1, len(habitaciones))
            fi     = hoy + timedelta(days=random.randint(0, 150))
            noches = random.randint(1, 7)
            fo     = fi + timedelta(days=noches)
            estado = random.choices(["confirmada","cancelada","completada"], weights=[0.5,0.2,0.3])[0]
            precio_noche = float(habitaciones[id_hab-1][3])
            total  = round(precio_noche * noches, 2)
            reservas.append([rid, id_h, id_hab, fi.date().isoformat(), fo.date().isoformat(), estado, total])
        return huespedes, habitaciones, reservas
    _run(n, outdir, "hotel", build, validate_hotel,
         [("huespedes.csv",   ["id_huesped","nombre","email","documento"]),
          ("habitaciones.csv",["id_habitacion","numero","tipo","precio_noche"]),
          ("reservas.csv",    ["id_reserva","id_huesped","id_habitacion",
                                "fecha_checkin","fecha_checkout","estado","total"])],
         "Tema: hotel\nTablas (3):\n"
         "- huespedes(id_huesped PK, nombre, email, documento)\n"
         "- habitaciones(id_habitacion PK, numero, tipo {simple,doble,suite}, precio_noche DECIMAL)\n"
         "- reservas(id_reserva PK, id_huesped FK->huespedes.id_huesped,"
         " id_habitacion FK->habitaciones.id_habitacion,\n"
         "           fecha_checkin, fecha_checkout, estado {confirmada,cancelada,completada},"
         " total DECIMAL)\n"
         "Notas: total = precio_noche * noches; reservas canceladas sin cobro, etc.")

def gen_farmacia(n, outdir):
    hoy  = datetime(2024, 1, 1)
    cats = ["analgesico","antibiotico","vitamina","antiinflamatorio","antihistaminico"]
    def build(n):
        clientes = []
        for i in range(1, n+1):
            nombre = rand_name()
            clientes.append([i, nombre, rand_email(nombre, i), f"+57{random.randint(3000000000,3999999999)}"])
        medicamentos = [[i, f"Medicamento_{i}", random.choice(cats),
                         round(random.uniform(5.0, 80.0), 2)]
                        for i in range(1, max(8, int(n*0.08))+1)]
        precios = {m[0]: m[3] for m in medicamentos}
        ventas  = []
        for vid in range(1, int(1.5*n)+1):
            id_c  = random.randint(1, n)
            id_m  = random.randint(1, len(medicamentos))
            cant  = random.randint(1, 5)
            total = round(precios[id_m] * cant, 2)
            ventas.append([vid, id_c, id_m, _rand_date(hoy, 180), cant, total])
        return clientes, medicamentos, ventas
    _run(n, outdir, "farmacia", build, validate_farmacia,
         [("clientes.csv",     ["id_cliente","nombre","email","telefono"]),
          ("medicamentos.csv", ["id_medicamento","nombre","categoria","precio_unitario"]),
          ("ventas.csv",       ["id_venta","id_cliente","id_medicamento","fecha_venta",
                                 "cantidad","total"])],
         "Tema: farmacia\nTablas (3):\n"
         "- clientes(id_cliente PK, nombre, email, telefono)\n"
         "- medicamentos(id_medicamento PK, nombre, categoria"
         " {analgesico,antibiotico,vitamina,antiinflamatorio,antihistaminico}, precio_unitario DECIMAL)\n"
         "- ventas(id_venta PK, id_cliente FK->clientes.id_cliente,"
         " id_medicamento FK->medicamentos.id_medicamento,\n"
         "         fecha_venta, cantidad INT, total DECIMAL)\n"
         "Notas: total = cantidad * precio_unitario; ventas por categoria, clientes frecuentes, etc.")

def gen_banco(n, outdir):
    hoy = datetime(2024, 1, 1)
    def build(n):
        clientes = []
        for i in range(1, n+1):
            nombre = rand_name()
            clientes.append([i, nombre, rand_email(nombre, i, "banco.com"), f"CC{i:08d}"])
        cuentas = []
        for cid in range(1, int(1.1*n)+1):
            id_c = random.randint(1, n)
            tipo = random.choice(["corriente","ahorros"])
            saldo = round(random.uniform(0.0, 10000.0), 2)
            cuentas.append([cid, id_c, tipo, saldo])
        transacciones = []
        for tid in range(1, int(2.0*n)+1):
            id_cta = random.randint(1, len(cuentas))
            tipo   = random.choice(["deposito","retiro","transferencia"])
            monto  = round(random.uniform(10.0, 2000.0), 2)
            transacciones.append([tid, id_cta, _rand_date(hoy, 180), tipo, monto])
        return clientes, cuentas, transacciones
    _run(n, outdir, "banco", build, validate_banco,
         [("clientes.csv",      ["id_cliente","nombre","email","documento"]),
          ("cuentas.csv",       ["id_cuenta","id_cliente","tipo_cuenta","saldo"]),
          ("transacciones.csv", ["id_transaccion","id_cuenta","fecha","tipo","monto"])],
         "Tema: banco\nTablas (3):\n"
         "- clientes(id_cliente PK, nombre, email, documento)\n"
         "- cuentas(id_cuenta PK, id_cliente FK->clientes.id_cliente,"
         " tipo_cuenta {corriente,ahorros}, saldo DECIMAL)\n"
         "- transacciones(id_transaccion PK, id_cuenta FK->cuentas.id_cuenta, fecha,"
         " tipo {deposito,retiro,transferencia}, monto DECIMAL)\n"
         "Notas: saldo por tipo de cuenta, movimientos por mes, clientes con mas retiros, etc.")

def gen_cine(n, outdir):
    hoy     = datetime(2024, 3, 1)
    generos = ["accion","comedia","drama","terror","animacion"]
    salas   = ["A","B","C","D"]
    precios_sala = {"A": 12.0, "B": 12.0, "C": 15.0, "D": 18.0}
    def build(n):
        peliculas = [[i, f"Pelicula_{i}", random.choice(generos), random.randint(80, 150)]
                     for i in range(1, max(8, int(n*0.08))+1)]
        clientes  = []
        for i in range(1, n+1):
            nombre = rand_name()
            clientes.append([i, nombre, rand_email(nombre, i, "cine.com")])
        entradas = []
        for eid in range(1, int(1.4*n)+1):
            id_p  = random.randint(1, len(peliculas))
            id_c  = random.randint(1, n)
            sala  = random.choice(salas)
            precio = round(precios_sala[sala] * random.uniform(0.9, 1.1), 2)
            entradas.append([eid, id_p, id_c, _rand_date(hoy, 120), sala, precio])
        return peliculas, clientes, entradas
    _run(n, outdir, "cine", build, validate_cine,
         [("peliculas.csv", ["id_pelicula","titulo","genero","duracion_min"]),
          ("clientes.csv",  ["id_cliente","nombre","email"]),
          ("entradas.csv",  ["id_entrada","id_pelicula","id_cliente","fecha_funcion","sala","precio"])],
         "Tema: cine\nTablas (3):\n"
         "- peliculas(id_pelicula PK, titulo, genero {accion,comedia,drama,terror,animacion},"
         " duracion_min INT)\n"
         "- clientes(id_cliente PK, nombre, email)\n"
         "- entradas(id_entrada PK, id_pelicula FK->peliculas.id_pelicula,"
         " id_cliente FK->clientes.id_cliente,\n"
         "           fecha_funcion, sala {A,B,C,D}, precio DECIMAL)\n"
         "Notas: recaudo por genero, sala mas popular, peliculas con mas asistentes, etc.")

def gen_veterinaria(n, outdir):
    hoy      = datetime(2024, 2, 1)
    especies = ["perro","gato","ave","conejo","reptil"]
    diagnosticos = ["revision_general","vacunacion","desparasitacion",
                    "cirugia_menor","consulta_urgente","seguimiento"]
    def build(n):
        duenos = []
        for i in range(1, n+1):
            nombre = rand_name()
            duenos.append([i, nombre, rand_email(nombre, i, "vet.com"),
                           f"+57{random.randint(3000000000,3999999999)}"])
        mascotas = []
        for mid in range(1, int(1.3*n)+1):
            mascotas.append([mid, random.randint(1, n), f"Mascota_{mid}",
                             random.choice(especies), random.randint(0, 15)])
        consultas = []
        for cid in range(1, int(1.5*n)+1):
            id_m  = random.randint(1, len(mascotas))
            costo = round(random.uniform(30.0, 250.0), 2)
            consultas.append([cid, id_m, _rand_date(hoy, 150),
                              random.choice(diagnosticos), costo])
        return duenos, mascotas, consultas
    _run(n, outdir, "veterinaria", build, validate_veterinaria,
         [("duenos.csv",    ["id_dueno","nombre","email","telefono"]),
          ("mascotas.csv",  ["id_mascota","id_dueno","nombre_mascota","especie","edad_anios"]),
          ("consultas.csv", ["id_consulta","id_mascota","fecha_consulta","diagnostico","costo"])],
         "Tema: veterinaria\nTablas (3):\n"
         "- duenos(id_dueno PK, nombre, email, telefono)\n"
         "- mascotas(id_mascota PK, id_dueno FK->duenos.id_dueno, nombre_mascota,"
         " especie {perro,gato,ave,conejo,reptil}, edad_anios INT)\n"
         "- consultas(id_consulta PK, id_mascota FK->mascotas.id_mascota, fecha_consulta,"
         " diagnostico, costo DECIMAL)\n"
         "Notas: costo total por especie, diagnosticos mas frecuentes, duenos con mas mascotas, etc.")

def gen_supermercado(n, outdir):
    hoy  = datetime(2024, 1, 1)
    cats = ["lacteos","carnes","bebidas","frutas","limpieza","panaderia"]
    def build(n):
        clientes  = []
        for i in range(1, n+1):
            nombre = rand_name()
            clientes.append([i, nombre, rand_email(nombre, i, "super.com")])
        productos = [[i, f"Producto_{i}", random.choice(cats),
                      round(random.uniform(1.5, 50.0), 2)]
                     for i in range(1, max(10, int(n*0.1))+1)]
        precios   = {p[0]: p[3] for p in productos}
        compras   = []
        for cid in range(1, int(2.0*n)+1):
            id_c   = random.randint(1, n)
            id_p   = random.randint(1, len(productos))
            cant   = random.randint(1, 8)
            total  = round(precios[id_p] * cant, 2)
            compras.append([cid, id_c, id_p, _rand_date(hoy, 180), cant, total])
        return clientes, productos, compras
    _run(n, outdir, "supermercado", build, validate_supermercado,
         [("clientes.csv",  ["id_cliente","nombre","email"]),
          ("productos.csv", ["id_producto","nombre_producto","categoria","precio_unitario"]),
          ("compras.csv",   ["id_compra","id_cliente","id_producto","fecha","cantidad","total"])],
         "Tema: supermercado\nTablas (3):\n"
         "- clientes(id_cliente PK, nombre, email)\n"
         "- productos(id_producto PK, nombre_producto,"
         " categoria {lacteos,carnes,bebidas,frutas,limpieza,panaderia}, precio_unitario DECIMAL)\n"
         "- compras(id_compra PK, id_cliente FK->clientes.id_cliente,"
         " id_producto FK->productos.id_producto,\n"
         "          fecha, cantidad INT, total DECIMAL)\n"
         "Notas: total = cantidad * precio_unitario; categoria mas vendida, clientes frecuentes, etc.")

def gen_aeropuerto(n, outdir):
    hoy        = datetime(2024, 5, 1)
    ciudades   = ["Bogota","Medellin","Cali","Barranquilla","Cartagena",
                  "Bucaramanga","Pereira","Santa_Marta","Cucuta","Manizales"]
    aerolineas = ["Avianca","LatAm","Wingo","EasyFly","Satena"]
    precios_clase = {"economica": (80.0, 300.0), "ejecutiva": (300.0, 700.0), "primera": (700.0, 1500.0)}
    def build(n):
        pasajeros = []
        for i in range(1, n+1):
            nombre = rand_name()
            pasajeros.append([i, nombre, rand_email(nombre, i, "viajes.com"), f"PA{i:07d}"])
        vuelos = []
        for i in range(1, max(10, int(n*0.1))+1):
            origen, destino = random.sample(ciudades, 2)
            vuelos.append([i, origen, destino, random.choice(aerolineas)])
        reservas = []
        for rid in range(1, int(1.3*n)+1):
            id_p   = random.randint(1, n)
            id_v   = random.randint(1, len(vuelos))
            clase  = random.choices(["economica","ejecutiva","primera"], weights=[0.7,0.2,0.1])[0]
            lo, hi = precios_clase[clase]
            precio = round(random.uniform(lo, hi), 2)
            reservas.append([rid, id_p, id_v, _rand_date(hoy, 180), clase, precio])
        return pasajeros, vuelos, reservas
    _run(n, outdir, "aeropuerto", build, validate_aeropuerto,
         [("pasajeros.csv", ["id_pasajero","nombre","email","documento"]),
          ("vuelos.csv",    ["id_vuelo","origen","destino","aerolinea"]),
          ("reservas.csv",  ["id_reserva","id_pasajero","id_vuelo","fecha_vuelo","clase","precio"])],
         "Tema: aeropuerto\nTablas (3):\n"
         "- pasajeros(id_pasajero PK, nombre, email, documento)\n"
         "- vuelos(id_vuelo PK, origen, destino, aerolinea)\n"
         "- reservas(id_reserva PK, id_pasajero FK->pasajeros.id_pasajero,"
         " id_vuelo FK->vuelos.id_vuelo,\n"
         "           fecha_vuelo, clase {economica,ejecutiva,primera}, precio DECIMAL)\n"
         "Notas: recaudo por aerolinea, rutas mas populares, precio promedio por clase, etc.")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Generador aleatorio para Taller SQL (3 tablas, 9 temas)")
    ap.add_argument("tema", choices=[
        "ecommerce","biblioteca","clinica","universidad","eventos",
        "gimnasio","transporte","streaming","restaurante",
        "hotel","farmacia","banco","cine","veterinaria","supermercado","aeropuerto",
    ])
    ap.add_argument("--n",    type=int, default=120, help="Tamaño base (filas de entidad principal)")
    ap.add_argument("--out",  help="Carpeta de salida (opcional)")
    ap.add_argument("--seed", type=int, default=None, help="Semilla aleatoria (opcional)")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    outdir = args.out or f"./datos_{args.tema}"
    os.makedirs(outdir, exist_ok=True)

    gens = {
        "ecommerce":   gen_ecommerce,
        "biblioteca":  gen_biblioteca,
        "clinica":     gen_clinica,
        "universidad": gen_universidad,
        "eventos":     gen_eventos,
        "gimnasio":    gen_gimnasio,
        "transporte":  gen_transporte,
        "streaming":   gen_streaming,
        "restaurante": gen_restaurante,
        "hotel":       gen_hotel,
        "farmacia":    gen_farmacia,
        "banco":       gen_banco,
        "cine":        gen_cine,
        "veterinaria": gen_veterinaria,
        "supermercado":gen_supermercado,
        "aeropuerto":  gen_aeropuerto,
    }
    gens[args.tema](args.n, outdir)
    print(f"Datos generados en: {outdir}  (tema={args.tema}, n={args.n})")

if __name__ == "__main__":
    main()
