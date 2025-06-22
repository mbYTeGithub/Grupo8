import requests
import json
import time

# Estructura base del mensaje que se enviará a la API
chat = {
    "message": {
        "text": "",
        "chat": {"id": 1}
    },
    "type": 1
}

# URL del endpoint de la API
url = "http://127.0.0.1:8000/messages"

# Cabeceras HTTP para la solicitud
headers = {
    "Content-Type": "application/json",
    "token": ""  # Token de autenticación si se requiere
}

def input_user():
    """
    Solicita texto al usuario por consola y lo retorna.
    """
    print("\n-- Texto usuario: ")
    texto = input()
    return texto

while True:
    # 1. Leer entrada del usuario
    texto = input_user()

    # 2. Actualizar el campo de texto del mensaje
    chat["message"]["text"] = texto

    # 3. Serializar el payload a JSON
    try:
        payload = json.dumps(chat)
    except (TypeError, ValueError) as e:
        print(f"❌ Error al serializar el payload a JSON: {e}")
        continue

    # 4. Medir tiempo de envío
    tiempo_inicial = time.time()

    # 5. Enviar la solicitud POST a la API
    print(f"Enviando payload: {payload}")
    try:
        response = requests.post(url, headers=headers, data=payload)
        # Verificar errores HTTP (4xx, 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud HTTP: {e}")
        continue

    # 6. Parsear la respuesta JSON
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear la respuesta JSON: {e}")
        continue

    # 7. Medir tiempo de respuesta
    tiempo_final = time.time()
    tiempo_total = tiempo_final - tiempo_inicial

    # 8. Mostrar resultado y métricas
    if isinstance(result, dict) and "response" in result:
        print(f"\n✅ Respuesta de la API:\n{result['response']}")
    else:
        print(f"\n❌ Estructura inesperada en la respuesta: {result}")

    print(f"⏱ Tiempo de respuesta: {tiempo_total:.2f} segundos\n")