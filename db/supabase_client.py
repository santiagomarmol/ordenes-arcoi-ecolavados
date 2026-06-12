from supabase import create_client, Client
from config import Config

def get_supabase() -> Client:
    """
    Crea y devuelve un cliente Supabase fresco por cada llamada.
    No uses una instancia global — evita problemas de estado
    compartido entre peticiones concurrentes.
    """
    Config.validate()
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY) 