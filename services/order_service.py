from db.supabase_client import get_supabase

VALID_STATUSES = ['Pendiente', 'En ruta', 'Entregado', 'Cancelado']

VALID_TRANSITIONS = {
    'Pendiente':  ['En ruta', 'Cancelado'],
    'En ruta':    ['Entregado', 'Cancelado'],
    'Entregado':  [],
    'Cancelado':  [],
}

def get_all_orders(status_filter=None):
    client = get_supabase()
    query = client.table('orders').select('*').order('created_at', desc=True)
    if status_filter and status_filter in VALID_STATUSES:
        query = query.eq('status', status_filter)
    return query.execute().data

def get_order_by_id(order_id):
    client = get_supabase()
    result = client.table('orders').select('*').eq('id', order_id).execute()
    return result.data[0] if result.data else None

def create_order(client_name, driver_name, order_date, observations=None):
    # Guardia de campos obligatorios
    errors = []
    if not client_name or not client_name.strip():
        errors.append("El nombre del cliente es obligatorio.")
    if not driver_name or not driver_name.strip():
        errors.append("El nombre del conductor es obligatorio.")
    if not order_date:
        errors.append("La fecha de la orden es obligatoria.")
    if errors:
        raise ValueError(" | ".join(errors))

    client = get_supabase()
    payload = {
        'client_name':  client_name.strip(),
        'driver_name':  driver_name.strip(),
        'order_date':   order_date,
        'status':       'Pendiente',
        'observations': observations or None,
    }
    return client.table('orders').insert(payload).execute().data[0]

def update_order(order_id, client_name, driver_name, order_date,
                 new_status, observations=None):
    order = get_order_by_id(order_id)
    if not order:
        raise ValueError("Orden no encontrada.")

    current_status = order['status']
    if new_status != current_status:
        allowed = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Transición inválida: '{current_status}' → '{new_status}'."
            )

    client = get_supabase()
    payload = {
        'client_name':  client_name,
        'driver_name':  driver_name,
        'order_date':   order_date,
        'status':       new_status,
        'observations': observations or None,
    }
    result = client.table('orders').update(payload).eq('id', order_id).execute()

    if not result.data:
        raise ValueError("La orden no pudo actualizarse. Es posible que ya no exista.")

    return result.data[0]

def cancel_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        raise ValueError("Orden no encontrada.")
    if order['status'] == 'Cancelado':
        raise ValueError("La orden ya está cancelada.")

    client = get_supabase()
    return client.table('orders').update(
        {'status': 'Cancelado'}
    ).eq('id', order_id).execute().data[0]