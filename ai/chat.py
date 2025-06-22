# ai.py
import json
import re
import requests
from openai import OpenAI
import config
from bd.sql import buscar_suelos_por_pais_region, buscar_cultivos_por_tipo
from bd.vector import store_vector_in_redis, find_vector_in_redis

history = {}
conversacion_texto = ""

def generate_text(prompt, chat_id):
    global conversacion_texto
    print (f"generate_text -- 1 {config.redis_host}")
    client = OpenAI(api_key=config.gpt_key)

    # Construir prompt del sistema
    system_prompt = {
        "role": "system",
        "content": config.ai_prompt_system + "\n\nCONTEXTO:\n" + prompt
    }
    print ("generate_text -- 2")
    # Inicializar historial si es necesario
    if chat_id not in history:
        history[chat_id] = []
    print ("generate_text -- 3")
    # Limitar historial
    max_pairs = 4
    if len(history[chat_id]) > max_pairs * 2:
        history[chat_id] = history[chat_id][-(max_pairs * 2):]
    print ("generate_text -- 4")
    # Construir mensaje inicial
    messages = [system_prompt] + history[chat_id] + [{"role": "user", "content": prompt}]
    print(f"mensaje enviado: {messages} ")
    print(f"--- Enviado a OpenAI (Chat ID: {chat_id}) ---")
    print(json.dumps(messages, indent=2, ensure_ascii=False))
    print("--------------------------------------------")
    conversacion_texto = conversacion_texto + prompt + "\n\n"
    try:
        print("crea el response...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
            max_tokens=1000
        )
        print("envió el response...")
        reply = response.choices[0].message.content
        answer = json.dumps(reply)
        print(f"obtiene resultado... {reply}")
        # Intentar extraer JSON clínico
        #json_pattern = r"\{[\s\S]*?\}"
        json_pattern = r'^\s*\{.*\}\s*$'

        try:
            match = re.search(json_pattern, reply, re.DOTALL)
        except Exception as e:
            match = None

        params = {}
        predict_result = None
        base_conocimiento_result = None
        final_response = reply

        conversacion_texto = conversacion_texto + reply + "\n\n"

        print(f"match: {match}")

        if match:
            try:
                print("paso 2")
                params = json.loads(match.group())
                print("paso 3")
                print("🎯 JSON con información detectado:", params)
               
                base_conocimiento_historico = None
                base_conocimiento_result = buscar_cultivos_por_json(params)
                base_conocimiento_historico = buscar_historial(conversacion_texto)
                print(f"conocimiento historico .. {base_conocimiento_historico}")
                
                # Generar nuevo mensaje a OpenAI con la predicción
                if base_conocimiento_result:
                    interpret_prompt = config.ai_prompt_system2 + config.ai_prompt_system3 +  f"""
                        {json.dumps(params, indent=2)}""" + config.ai_prompt_system4 + f"""
                        {json.dumps(base_conocimiento_result, indent=2)}""" + config.ai_prompt_system5 + base_conocimiento_historico
                    
                    print(f"prompt final: {interpret_prompt}")
                    final_response = generate_final_output(interpret_prompt, chat_id)
                    conversacion_texto = conversacion_texto + final_response + "\n\n"
                    store_chat_history(chat_id, conversacion_texto)
                    conversacion_texto = ""
                    
            except json.JSONDecodeError as e:
                print("❌ JSON inválido:", e)

        # Guardar historial
        history[chat_id].append({"role": "user", "content": prompt})
        history[chat_id].append({"role": "assistant", "content": answer})

        return {
            "response": final_response,
            "params": params,
            "predict": predict_result
        }

    except Exception as e:
        print(f"❌ Error en llamada a OpenAI: {e}")
        return {
            "response": "Lo siento, ocurrió un error al procesar tu solicitud.",
            "params": {},
            "predict": None
        }


def hacer_prediccion_si_hay_datos(params):
    campos = ["Age", "RestingBP", "Cholesterol", "Oldpeak", "FastingBS", "MaxHR"]
    if not all(k in params for k in campos):
        return None

    url = "https://ai-app-a441e0d147d0.herokuapp.com/predict"
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en la predicción:", e)
        return None

def buscar_suelos_por_json(json_input):
    try:
        # Asegurarse de que el input es un diccionario
        if isinstance(json_input, str):
            json_input = json.loads(json_input)

        # Extraer los valores de 'pais' y 'region' del JSON
        pais = json_input.get('pais')
        region = json_input.get('region')

        # Verificar que ambos valores estén presentes
        if not pais or not region:
            return json.dumps({"error": "Faltan 'pais' o 'region' en el JSON"}, ensure_ascii=False)

        # Llamar a la función buscar_suelos_por_pais_region
        resultados_json = buscar_suelos_por_pais_region(pais, region)

        return resultados_json

    except json.JSONDecodeError as e:
        return json.dumps({"error": "JSON inválido"}, ensure_ascii=False)

def buscar_cultivos_por_json(json_input):
    try:
        # Asegurarse de que el input es un diccionario
        if isinstance(json_input, str):
            json_input = json.loads(json_input)

        # Extraer el valor de 'tipo_cultivo' del JSON
        tipo_cultivo = json_input.get('tipo_cultivo')

        # Verificar que el valor esté presente
        if not tipo_cultivo:
            return json.dumps({"error": "Falta 'tipo_cultivo' en el JSON"}, ensure_ascii=False)

        # Llamar a la función buscar_cultivos_por_tipo
        resultados_json = buscar_cultivos_por_tipo(tipo_cultivo)

        return resultados_json

    except json.JSONDecodeError as e:
        return json.dumps({"error": "JSON inválido"}, ensure_ascii=False)

def generate_final_output(text_prompt, chat_id):
    client = OpenAI(api_key=config.gpt_key)

    messages = [
        {"role": "system", "content": "Eres un agente experto en nutrición vegetal agronomica. Usa emojis y un tono positivo."},
        {"role": "user", "content": text_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generando salida final:", e)
        return "La predicción se realizó, pero no se pudo generar una explicación textual."

def store_chat_history(chat_id, message):
    # Convertir el mensaje a un vector y almacenarlo en Redis
    document_id = f"chat_{chat_id}_message_{len(history[chat_id])}"
    store_vector_in_redis(message, document_id)

def buscar_historial(menssage):
    return find_vector_in_redis(menssage)

def collect_user_feedback(chat_id, feedback):
    # Almacenar el feedback en Redis o en otra base de datos
    document_id = f"chat_{chat_id}_feedback"
    store_vector_in_redis(feedback, document_id)