from config import Config
from db.supabase_client import get_supabase

def test():
    # 1. Valida que las variables de entorno existen
    Config.validate()
    print("✓ Variables de entorno cargadas")

    # 2. Intenta conectar
    client = get_supabase()
    print("✓ Cliente Supabase creado")

    # 3. Hace una lectura real a la tabla orders
    response = client.table("orders").select("*").limit(1).execute()
    print("✓ Conexión exitosa. Registros encontrados:", len(response.data))

if __name__ == "__main__":
    test()