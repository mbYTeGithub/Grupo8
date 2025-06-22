"""
main.py

API REST con FastAPI para exponer el endpoint /messages que maneja 
interacciones de chat con OpenAI. 
- Soporta CORS
- Define endpoints GET / (prueba) y POST /messages
- Maneja errores de validación de payload y del servidor
"""

from openai import OpenAI 
import os
import requests
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from bd.vector import find_vector_in_redis
from ai.chat import generate_text
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import config

# Inicializar el cliente de OpenAI
try:
    client = OpenAI(api_key=config.gpt_key)
except Exception as e:
    print(f"⚠️ No se pudo inicializar OpenAI: {e}")
    client = None

app = FastAPI()

# Configurar CORS para permitir todas las fuentes (ajustar según tus necesidades)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTOR_FIELD_NAME = 'content_vector'

@app.get("/")
async def init():
    """
    Endpoint de prueba.
    Retorna un mensaje de estado para verificar que el servicio está activo.
    """
    return {"status": "ok", "message": "Servicio de chat IA en línea"}

@app.post("/messages")
def messages(payload: dict = Body(...)):
    """
    Endpoint principal que recibe un payload con la siguiente estructura:
      {
        "message": {
            "text": "...",
            "chat": {"id": <int>}
        },
        "type": <int>
      }
    Valida los campos requeridos, construye un prompt, llama a generate_text()
    y retorna {"response": <resultado>}. En caso de error, retorna el código adecuado.
    """
    # 1. Validar y extraer campos del payload
    try:
        message_block = payload["message"]
        chat_id = message_block["chat"]["id"]
        message = message_block["text"]
        typeApp = payload.get("type")
    except KeyError as e:
        # Falta un campo obligatorio
        raise HTTPException(status_code=400, detail=f"Campo faltante en payload: {e}")
    except Exception as e:
        # Payload malformado
        raise HTTPException(status_code=400, detail=f"Payload inválido: {e}")

    print(f"📩 Recibido mensaje (chat_id={chat_id}, type={typeApp}): {message}")

    # 2. Construir prompt y llamar a la función de IA
    try:
        prompt = f"pregunta: {message}"
        response = generate_text(prompt, chat_id)
        # Retornar la respuesta para el cliente
        return {"response": response}
    except Exception as e:
        # Error interno procesando la solicitud
        print(f"❌ Error procesando el mensaje: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error interno del servidor"}
        )

if __name__ == "__main__":
    """
    Punto de entrada: ejecuta el servidor Uvicorn cuando el script se corre directamente.
    """
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"⚠️ Error iniciando el servidor: {e}")