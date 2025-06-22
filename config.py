import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

redis_host     = os.getenv("REDIS_HOST")
redis_port     = os.getenv("REDIS_PORT")
redis_db       = os.getenv("REDIS_DB")
redis_username = os.getenv("REDIS_USERNAME")
redis_password = os.getenv("REDIS_PASSWORD")
redis_index    = os.getenv("REDIS_INDEX")
ai_prompt_system   = os.getenv("AI_PROMPT_SYSTEM", "")
ai_prompt_system2  = os.getenv("AI_PROMPT_SYSTEM2", "")
ai_prompt_system3  = os.getenv("AI_PROMPT_SYSTEM3", "")
ai_prompt_system4  = os.getenv("AI_PROMPT_SYSTEM4", "")
ai_prompt_system5  = os.getenv("AI_PROMPT_SYSTEM5", "")
gpt_key            = os.getenv("OPENAI_API_KEY")
welcome_message    = os.getenv("WELCOME_MESSAGE")