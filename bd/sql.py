import sqlite3
import json
import pandas as pd
db_path = 'bd/data/base_grupo8.db'

def buscar_suelos_por_pais_region(pais, region):
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ejecutar la consulta SQL
    query = """
    SELECT * FROM tipo_suelos_globales
    WHERE pais = UPPER(?) AND region = UPPER(?)
    """
    cursor.execute(query, (pais, region))

    # Obtener los resultados
    rows = cursor.fetchall()

    # Obtener los nombres de las columnas
    column_names = [description[0] for description in cursor.description]

    # Convertir los resultados a una lista de diccionarios
    resultados = [dict(zip(column_names, row)) for row in rows]

    # Cerrar la conexión
    conn.close()

    # Convertir los resultados a JSON
    return json.dumps(resultados, ensure_ascii=False, indent=4)

def buscar_cultivos_por_tipo(tipo_cultivo):
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ejecutar la consulta SQL
    query = """
    SELECT * FROM cultivos_nutricion
    WHERE tipo_cultivo = UPPER(?)
    """
    cursor.execute(query, (tipo_cultivo,))

    # Obtener los resultados
    rows = cursor.fetchall()

    # Obtener los nombres de las columnas
    column_names = [description[0] for description in cursor.description]

    # Convertir los resultados a una lista de diccionarios
    resultados = [dict(zip(column_names, row)) for row in rows]

    # Cerrar la conexión
    conn.close()

    # Convertir los resultados a JSON
    return json.dumps(resultados, ensure_ascii=False, indent=4)

def importar_csv_a_sqlite(db_path, csv_path, table_name):
    # Leer el archivo CSV usando pandas
    df = pd.read_csv(csv_path)

    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(db_path)

    # Importar el DataFrame a la tabla SQLite
    df.to_sql(table_name, conn, if_exists='append', index=False)

    # Cerrar la conexión
    conn.close()
