import numpy as np
from openai import OpenAI
from redis import Redis
from redis.commands.search.query import Query
import json
import config

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis as rd
from langchain.schema import Document
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# Cliente de OpenAI para generar embeddings
client = OpenAI(api_key=config.gpt_key)

# Nombre del campo vectorial en los hashes de Redis
VECTOR_FIELD_NAME = 'content_vector'
# Dimensión de los embeddings del modelo text-embedding-ada-002
EMBEDDING_DIMENSION = 1536

def find_vector_in_redis(query):
    """
    Realiza una búsqueda semántica en Redis usando RediSearch.
    1. Genera embedding de la consulta con OpenAI.
    2. Convierte el embedding a bytes (array de float32).
    3. Ejecuta una consulta KNN en el índice vectorial.
    Retorna el contenido del documento más similar.
    """
    # 1. Conectar a Redis
    url = f"redis://{config.redis_username}:{config.redis_password}" \
          f"@{config.redis_host}:{config.redis_port}/{config.redis_db}"
    try:
        r = Redis.from_url(url=url)
    except Exception as e:
        raise ConnectionError(f"Error conectando a Redis: {e}")

    top_k = 1

    # 2. Generar el embedding de la consulta
    try:
        embedding_response = client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
    except Exception as e:
        raise RuntimeError(f"Error generando embedding: {e}")

    # 3. Convertir el embedding a bytes de tipo float32
    try:
        embedded_query = np.array(
            embedding_response.data[0].embedding,
            dtype=np.float32
        ).tobytes()
    except Exception as e:
        raise ValueError(f"Error procesando embedding a bytes: {e}")

    # 4. Construir y ejecutar la consulta KNN en RediSearch
    try:
        q = (
            Query(f'*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]')
            .sort_by('vector_score')
            .paging(0, top_k)
            .return_fields('content')
            .dialect(2)
        )
        results = r.ft(config.redis_index).search(q, query_params={"vec_param": embedded_query})
    except Exception as e:
        raise RuntimeError(f"Error en RediSearch KNN: {e}")

    # 5. Verificar resultados
    if not results.docs:
        raise LookupError("No se encontraron documentos similares.")

    # Retornar el contenido del documento más cercano
    return results.docs[0].content

def store_vector_in_redis(corpus, id_document):
    """
    Crea un embedding de `corpus` y lo almacena en Redis Vector Store:
    1. Inicializa el generador de embeddings de OpenAI.
    2. Crea un objeto Document con el texto y metadatos.
    3. Inserta el documento en Redis bajo el índice config.redis_index.
    Retorna el objeto vectorstore para operaciones posteriores.
    """
    # 1. Inicializar embeddings
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=config.gpt_key)
    except Exception as e:
        raise RuntimeError(f"Error inicializando OpenAIEmbeddings: {e}")

    # 2. Crear documento LangChain
    try:
        documento = Document(page_content=corpus, metadata={"id": id_document})
    except Exception as e:
        raise ValueError(f"Error creando Document: {e}")

    docs = [documento]

    # 3. Almacenar en Redis Vector Store
    redis_url = f"redis://{config.redis_username}:{config.redis_password}" \
                f"@{config.redis_host}:{config.redis_port}/{config.redis_db}"
    try:
        vectorstore = rd.from_documents(
            docs,
            embeddings,
            redis_url=redis_url,
            index_name=config.redis_index
        )
    except Exception as e:
        raise RuntimeError(f"Error almacenando en Redis Vector Store: {e}")

    return vectorstore