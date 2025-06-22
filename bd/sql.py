import sqlite3
import json
import pandas as pd

# Ruta a la base de datos SQLite
db_path = 'bd/data/base_grupo8.db'

def buscar_suelos_por_pais_region(pais, region):
    """
    Busca en la tabla 'tipo_suelos_globales' registros que coincidan
    con el país y la región proporcionados (case-insensitive).
    Retorna un JSON con los registros encontrados o un mensaje de error.
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Consulta parametrizada para evitar inyección de SQL
        query = """
        SELECT * FROM tipo_suelos_globales
        WHERE pais = UPPER(?) AND region = UPPER(?)
        """
        cursor.execute(query, (pais, region))
        rows = cursor.fetchall()

        # Obtener nombres de columnas para mapear los resultados
        column_names = [description[0] for description in cursor.description]
        resultados = [dict(zip(column_names, row)) for row in rows]

    except sqlite3.Error as e:
        # En caso de error en la consulta, retornar un JSON con detalles
        return json.dumps(
            {"error": "Error al consultar tipo_suelos_globales", "detalle": str(e)},
            ensure_ascii=False, indent=4
        )
    finally:
        # Cerrar la conexión si fue abierta
        try:
            conn.close()
        except:
            pass

    # Retornar los resultados en formato JSON
    return json.dumps(resultados, ensure_ascii=False, indent=4)


def buscar_cultivos_por_tipo(tipo_cultivo):
    """
    Busca en la tabla 'cultivos_nutricion' registros que coincidan
    con el tipo de cultivo proporcionado (case-insensitive).
    Retorna un JSON con los registros encontrados o un mensaje de error.
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Consulta parametrizada
        query = """
        SELECT * FROM cultivos_nutricion
        WHERE tipo_cultivo = UPPER(?)
        """
        cursor.execute(query, (tipo_cultivo,))
        rows = cursor.fetchall()

        # Obtener nombres de columnas para mapear los resultados
        column_names = [description[0] for description in cursor.description]
        resultados = [dict(zip(column_names, row)) for row in rows]

    except sqlite3.Error as e:
        # En caso de error en la consulta, retornar un JSON con detalles
        return json.dumps(
            {"error": "Error al consultar cultivos_nutricion", "detalle": str(e)},
            ensure_ascii=False, indent=4
        )
    finally:
        # Cerrar la conexión si fue abierta
        try:
            conn.close()
        except:
            pass

    # Retornar los resultados en formato JSON
    return json.dumps(resultados, ensure_ascii=False, indent=4)


def importar_csv_a_sqlite(db_path_arg, csv_path, table_name):
    """
    Importa un archivo CSV a la tabla SQLite especificada.
    - db_path_arg: ruta al archivo de base de datos
    - csv_path: ruta al archivo CSV a importar
    - table_name: nombre de la tabla destino
    """
    # Leer el archivo CSV usando pandas
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo CSV '{csv_path}': {e}")

    # Escribir o anexar el DataFrame a la tabla SQLite
    try:
        conn = sqlite3.connect(db_path_arg)
        df.to_sql(table_name, conn, if_exists='append', index=False)
    except sqlite3.Error as e:
        raise RuntimeError(f"Error al insertar datos en la tabla '{table_name}': {e}")
    finally:
        # Cerrar la conexión si fue abierta
        try:
            conn.close()
        except:
            pass