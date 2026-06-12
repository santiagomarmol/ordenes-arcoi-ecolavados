from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
import services.order_service as svc

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

STATUSES = ['Pendiente', 'En ruta', 'Entregado', 'Cancelado']

# ── Listado ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    status_filter = request.args.get('status', '')
    orders = svc.get_all_orders(status_filter or None)
    return render_template('index.html',
                           orders=orders,
                           statuses=STATUSES,
                           current_filter=status_filter)

# ── Crear ──────────────────────────────────────────────────────────────────

@app.route('/orders/new', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        try:
            svc.create_order(
                client_name  = request.form['client_name'].strip(),
                driver_name  = request.form['driver_name'].strip(),
                order_date   = request.form['order_date'],
                observations = request.form.get('observations', '').strip(),
            )
            flash('Orden creada exitosamente.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al crear la orden: {e}', 'error')

    return render_template('form.html', order=None, statuses=STATUSES)

# ── Editar ─────────────────────────────────────────────────────────────────

@app.route('/orders/<order_id>/edit', methods=['GET', 'POST'])
def edit_order(order_id):
    order = svc.get_order_by_id(order_id)
    if not order:
        flash('Orden no encontrada.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            svc.update_order(
                order_id     = order_id,
                client_name  = request.form['client_name'].strip(),
                driver_name  = request.form['driver_name'].strip(),
                order_date   = request.form['order_date'],
                new_status   = request.form['status'],
                observations = request.form.get('observations', '').strip(),
            )
            flash('Orden actualizada.', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('form.html', order=order, statuses=STATUSES)

# ── Cancelar ───────────────────────────────────────────────────────────────

@app.route('/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    try:
        svc.cancel_order(order_id)
        flash('Orden cancelada.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('index'))

# ── Arranque ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)