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

client = OpenAI(api_key=config.gpt_key)

VECTOR_FIELD_NAME = 'content_vector'
EMBEDDING_DIMENSION = 1536  # Dimensión de los embeddings de text-embedding-ada-002

def find_vector_in_redis(query):

    url = "redis://{}:{}@{}:{}/{}".format(
        config.redis_username,
        config.redis_password,
        config.redis_host,
        config.redis_port,
        config.redis_db
    )

    r = Redis.from_url(url=url)
    top_k = 1

    # Crear embedding con la sintaxis correcta
    embedding_response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"  # Parámetro corregido
    )
    
    # Acceder al embedding correctamente
    embedded_query = np.array(
        embedding_response.data[0].embedding,  # Sintaxis corregida
        dtype=np.float32
    ).tobytes()

    # Preparar la query
    q = Query(f'*=>[KNN {top_k} @{VECTOR_FIELD_NAME} $vec_param AS vector_score]'
            ).sort_by('vector_score').paging(0, top_k).return_fields(
                'filename', 'text_chunk', 'text_chunk_index', 'content'
            ).dialect(2)
    
    params_dict = {"vec_param": embedded_query}

    # Ejecutar la consulta
    results = r.ft(config.redis_index).search(q, query_params=params_dict)
    print(f"resultados {results.docs[0]['content']}")
    
    return results.docs[0]['content']

def store_vector_in_redis(corpus, id_document):

     # Generar embedding
    embeddings = OpenAIEmbeddings(
        openai_api_key=config.gpt_key
    )

    documentos = []
    documento = Document(page_content=corpus)

    print(documento)

    documentos.append(documento)
    vectorstore = rd.from_documents(
    documentos,
    embeddings,
    redis_url=f"redis://default:{config.redis_password}@{config.redis_host}:{config.redis_port}/0",
    index_name=config.redis_index
    )
