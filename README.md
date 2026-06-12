# Gestor de Órdenes de Transporte

Aplicación web construida con Python + Flask + Supabase para gestionar órdenes de transporte con seguimiento de estados.

---

## Cómo correr el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd transport-orders
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv

# Linux / Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto (ver sección Variables de entorno).

### 5. Arrancar el servidor

```bash
python app.py
```

Abre `http://127.0.0.1:5000` en el browser.

---

## Variables de entorno (.env)

```env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
FLASK_SECRET_KEY=una-clave-larga-y-aleatoria
FLASK_DEBUG=True
```

| Variable | Dónde obtenerla |
|---|---|
| `SUPABASE_URL` | Supabase dashboard → Settings → API → Project URL |
| `SUPABASE_SERVICE_KEY` | Supabase dashboard → Settings → API → service_role key |
| `FLASK_SECRET_KEY` | Cualquier string largo y aleatorio (úsalo para firmar sesiones) |
| `FLASK_DEBUG` | `True` en desarrollo, `False` en producción |

> **Importante:** Usa siempre la `service_role` key en el backend, nunca la `anon` key. Nunca subas `.env` al repositorio.

---

## Estructura de archivos

```
transport-orders/
│
├── .env                        ← Credenciales locales (no va al repo)
├── .gitignore
├── requirements.txt
├── config.py                   ← Lee .env y expone variables a la app
├── app.py                      ← Punto de entrada Flask + todas las rutas
│
├── db/
│   ├── __init__.py
│   └── supabase_client.py      ← Fábrica del cliente Supabase (una instancia por petición)
│
├── services/
│   ├── __init__.py
│   └── order_service.py        ← Lógica de negocio: validaciones, transiciones de estado, queries
│
├── templates/
│   ├── base.html               ← Layout base: navbar, flash messages, estilos
│   ├── index.html              ← Listado de órdenes + filtro por estado
│   └── form.html               ← Formulario reutilizable para crear y editar
│
└── static/
    └── style.css               ← CSS adicional (opcional)
```

---

## Esquema de la tabla en Supabase

**Tabla:** `orders`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | `uuid` | PK, `DEFAULT gen_random_uuid()` |
| `client_name` | `text` | `NOT NULL` |
| `driver_name` | `text` | `NOT NULL` |
| `order_date` | `date` | `NOT NULL` |
| `status` | `text` | `NOT NULL`, `DEFAULT 'Pendiente'`, CHECK en valores válidos |
| `observations` | `text` | nullable |
| `created_at` | `timestamptz` | `NOT NULL`, `DEFAULT now()` |
| `updated_at` | `timestamptz` | `NOT NULL`, `DEFAULT now()`, actualizado por trigger |

**CHECK constraint de estados:**

```sql
ALTER TABLE orders
  ADD CONSTRAINT orders_status_check
  CHECK (status IN ('Pendiente', 'En ruta', 'Entregado', 'Cancelado'));
```

**Trigger para `updated_at`:**

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
```

**Flujo de estados:**

```
Pendiente → En ruta → Entregado
    ↓           ↓
 Cancelado   Cancelado
```

---

## Decisión técnica: Supabase sobre SQLite local

SQLite es simple y no requiere infraestructura, pero ata la base de datos al servidor donde corre Flask. Si el servidor se reinicia, se mueve, o escala horizontalmente, los datos son un problema de sincronización inmediato.

Supabase expone PostgreSQL como servicio REST: la base de datos vive independiente de la aplicación, tiene backups automáticos, permite acceso desde cualquier entorno (local, staging, producción) con las mismas credenciales, y no requiere administrar un servidor de base de datos. Para una app de gestión operativa donde la pérdida de datos tiene consecuencia real, esa separación no es opcional.
