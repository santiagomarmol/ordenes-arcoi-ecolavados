import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-insegura")
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    @classmethod
    def validate(cls):
        missing = [k for k, v in {
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_SERVICE_KEY": cls.SUPABASE_SERVICE_KEY,
        }.items() if not v]
        if missing:
            raise EnvironmentError(f"Variables de entorno faltantes: {missing}")