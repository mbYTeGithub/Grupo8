# ai/chat.py
"""
Módulo principal que maneja la interacción con OpenAI, mantiene historial
de conversaciones, extrae JSON de respuestas, consulta bases de datos SQLite
y Redis, y almacena el historial vectorizado.
"""

import json
import re
import requests
from openai import OpenAI
import config
from bd.sql import buscar_suelos_por_pais_region, buscar_cultivos_por_tipo
from bd.vector import store_vector_in_redis, find_vector_in_redis

# Historial de mensajes por chat_id
history = {}
# Texto completo de la conversación para vectorización
conversacion_texto = ""

def generate_text(prompt, chat_id):
    """
    Envía un prompt a OpenAI Chat completions, maneja historial en memoria,
    extrae JSON de la respuesta, realiza búsquedas en SQLite y Redis, y
    almacena el historial completo como vector en Redis.
    Retorna un dict con keys: response, params, predict.
    """
    global conversacion_texto

    # 1. Inicializar cliente de OpenAI
    try:
        client = OpenAI(api_key=config.gpt_key)
    except Exception as e:
        print(f"❌ Error inicializando OpenAI: {e}")
        return {"response": "Error interno de configuración.", "params": {}, "predict": None}

    # 2. Construir mensaje de sistema y usuario
    system_prompt = {
        "role": "system",
        "content": config.ai_prompt_system + "\n\nCONTEXTO:\n" + prompt
    }
    if chat_id not in history:
        history[chat_id] = []
    # Limitar historial a los últimos 4 pares (user+assistant)
    max_pairs = 4
    if len(history[chat_id]) > max_pairs * 2:
        history[chat_id] = history[chat_id][-(max_pairs * 2):]
    messages = [system_prompt] + history[chat_id] + [{"role": "user", "content": prompt}]

    # 3. Acumular texto de entrada para vectorización
    conversacion_texto += prompt + "\n\n"

    # 4. Llamar al modelo de OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=1000
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error en la llamada a OpenAI: {e}")
        return {"response": "Lo siento, ocurrió un error al procesar tu solicitud.", "params": {}, "predict": None}

    # 5. Guardar respuesta y acumular en texto de conversación
    answer = json.dumps(reply)
    conversacion_texto += reply + "\n\n"

    # 6. Intentar extraer JSON de la respuesta
    json_pattern = r'^\s*\{.*\}\s*$'
    match = None
    try:
        match = re.search(json_pattern, reply, re.DOTALL)
    except Exception as e:
        print(f"❌ Error buscando JSON en la respuesta: {e}")

    params = {}
    predict_result = None
    base_conocimiento_result = None
    final_response = reply

    # 7. Si hay JSON, procesar recomendaciones
    if match:
        try:
            params = json.loads(match.group())
        except json.JSONDecodeError as e:
            print(f"❌ JSON inválido: {e}")
        else:
            # 7a. Buscar recomendaciones de cultivos en SQLite
            try:
                base_conocimiento_result = buscar_cultivos_por_json(params)
            except Exception as e:
                print(f"❌ Error buscando cultivos: {e}")

            # 7b. Buscar en historial vectorial en Redis
            try:
                historial_vec = find_vector_in_redis(conversacion_texto)
            except Exception as e:
                print(f"❌ Error buscando historial vectorial: {e}")
                historial_vec = ""

            # 7c. Generar prompt final si hay datos de base de conocimiento
            if base_conocimiento_result:
                interpret_prompt = (
                    config.ai_prompt_system2
                    + config.ai_prompt_system3
                    + json.dumps(params, indent=2)
                    + config.ai_prompt_system4
                    + json.dumps(base_conocimiento_result, indent=2)
                    + config.ai_prompt_system5
                    + historial_vec
                )
                try:
                    final_response = generate_final_output(interpret_prompt, chat_id)
                except Exception as e:
                    print(f"❌ Error generando respuesta final: {e}")

                # 7d. Almacenar el historial completo como vector en Redis
                try:
                    store_chat_history(chat_id, conversacion_texto)
                except Exception as e:
                    print(f"❌ Error almacenando historial vectorial: {e}")

                # Resetear texto acumulado
                conversacion_texto = ""

    # 8. Actualizar historial en memoria
    history[chat_id].append({"role": "user", "content": prompt})
    history[chat_id].append({"role": "assistant", "content": answer})

    return {"response": final_response, "params": params, "predict": predict_result}


def buscar_suelos_por_json(json_input):
    """
    Extrae 'pais' y 'region' de un JSON y llama a buscar_suelos_por_pais_region.
    Retorna JSON con resultados o mensaje de error.
    """
    try:
        data = json_input if isinstance(json_input, dict) else json.loads(json_input)
        pais = data.get("pais")
        region = data.get("region")
        if not pais or not region:
            return json.dumps({"error": "Faltan 'pais' o 'region'"}, ensure_ascii=False)
        return buscar_suelos_por_pais_region(pais, region)
    except Exception as e:
        print(f"❌ Error en buscar_suelos_por_json: {e}")
        return json.dumps({"error": "Error interno"}, ensure_ascii=False)


def buscar_cultivos_por_json(json_input):
    """
    Extrae 'tipo_cultivo' de un JSON y llama a buscar_cultivos_por_tipo.
    Retorna JSON con resultados o mensaje de error.
    """
    try:
        data = json_input if isinstance(json_input, dict) else json.loads(json_input)
        tipo_cultivo = data.get("tipo_cultivo")
        if not tipo_cultivo:
            return json.dumps({"error": "Falta 'tipo_cultivo'"}, ensure_ascii=False)
        return buscar_cultivos_por_tipo(tipo_cultivo)
    except Exception as e:
        print(f"❌ Error en buscar_cultivos_por_json: {e}")
        return json.dumps({"error": "Error interno"}, ensure_ascii=False)


def generate_final_output(text_prompt, chat_id):
    """
    Envía un prompt de interpretación final a OpenAI para generar
    una explicación amigable. Retorna el texto o un mensaje de error.
    """
    try:
        client = OpenAI(api_key=config.gpt_key)
        messages = [
            {"role": "system", "content": "Eres un agente experto en nutrición vegetal agronomica. Usa emojis y un tono positivo."},
            {"role": "user", "content": text_prompt}
        ]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generando salida final: {e}")
        return "Ocurrió un error al generar la explicación."


def store_chat_history(chat_id, message):
    """
    Convierte el texto de la conversación en vector y lo almacena
    en Redis con store_vector_in_redis.
    """
    document_id = f"chat_{chat_id}_message_{len(history.get(chat_id, []))}"
    store_vector_in_redis(message, document_id)


def buscar_historial(message):
    """
    Realiza búsqueda semántica en Redis sobre la conversación acumulada.
    """
    return find_vector_in_redis(message)


def collect_user_feedback(chat_id, feedback):
    """
    Almacena el feedback del usuario en Redis para evaluación continua.
    """
    document_id = f"chat_{chat_id}_feedback"
    store_vector_in_redis(feedback, document_id)