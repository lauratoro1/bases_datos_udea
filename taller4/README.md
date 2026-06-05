# Taller 4 - MongoDB y APIs

## Descripción del Proyecto

Este proyecto consiste en consumir datos desde una API pública de Game of Thrones, almacenarlos en MongoDB y realizar análisis exploratorio utilizando Python y Pandas.


## API Utilizada

API:

https://thronesapi.com/

Endpoint utilizado:

https://thronesapi.com/api/v2/Characters



## Tecnologías Utilizadas

* Python
* MongoDB
* MongoDB Compass
* Pandas
* Matplotlib
* Jupyter Notebook
* PyMongo



## Funcionalidades

### Ingesta de Datos

* Conexión a MongoDB
* Creación de base de datos `taller4_db`
* Creación de colección `raw_data`
* Inserción de datos JSON raw

### Análisis Exploratorio

* Creación de DataFrame
* Inspección de datos
* Insights numéricos
* Visualizaciones


## Archivos del Proyecto


taller4/
│
├── ingesta.py
├── consultas.py
├── analisis_got.ipynb
├── requirements.txt
└── README.md


---

## Cómo Ejecutar

### 1. Crear entorno virtual

```bash id="jlwm14"
python -m venv .venv
```

### 2. Activar entorno virtual

```bash id="jlwme9"
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash id="jlwml8"
pip install -r requirements.txt
```

### 4. Ejecutar ingesta

```bash id="jlwmo4"
python ingesta.py
```

### 5. Abrir Jupyter Notebook

```bash id="jlwmc1"
jupyter notebook
```

---

## Base de Datos

* Base de datos: `taller4_db`
* Colección: `raw_data`

---

## Autor

Laura Maria Toro Montoya
