import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
# Asegúrate de crear un archivo '.env' en la raíz con las claves necesarias.
load_dotenv(dotenv_path=".env")

# --- Configuración de Redis ---
# Host de Redis (obligatorio)
redis_host = os.getenv("REDIS_HOST")
if not redis_host:
    raise EnvironmentError("Variable REDIS_HOST no definida")

# Puerto de Redis (opcional, por defecto 6379)
redis_port_str = os.getenv("REDIS_PORT", "6379")
try:
    redis_port = int(redis_port_str)
except ValueError:
    raise ValueError(f"REDIS_PORT inválido: '{redis_port_str}' no es un entero")

# Índice de la base de datos de Redis (opcional, por defecto 0)
redis_db = os.getenv("REDIS_DB", "0")

# Credenciales de Redis (pueden quedar vacías si no se usan)
redis_username = os.getenv("REDIS_USERNAME", "")
redis_password = os.getenv("REDIS_PASSWORD", "")

# Nombre del índice vectorial en Redis (obligatorio)
redis_index = os.getenv("REDIS_INDEX")
if not redis_index:
    raise EnvironmentError("Variable REDIS_INDEX no definida")

# --- Configuración de OpenAI ---
# Clave de API de OpenAI (obligatoria)
gpt_key = os.getenv("OPENAI_API_KEY")
if not gpt_key:
    raise EnvironmentError("Variable OPENAI_API_KEY no definida")

# --- Prompts del sistema para la IA ---
# Estos prompts se usan como contexto inicial para las conversaciones
ai_prompt_system   = os.getenv("AI_PROMPT_SYSTEM", "")
ai_prompt_system2  = os.getenv("AI_PROMPT_SYSTEM2", "")
ai_prompt_system3  = os.getenv("AI_PROMPT_SYSTEM3", "")
ai_prompt_system4  = os.getenv("AI_PROMPT_SYSTEM4", "")
ai_prompt_system5  = os.getenv("AI_PROMPT_SYSTEM5", "")

# --- Mensajes adicionales ---
# Mensaje de bienvenida al usuario (opcional)
welcome_message    = os.getenv("WELCOME_MESSAGE", "")