from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import SessionLocal, get_db
from models import Usuario, Producto
from auth import hash_password, verify_password
import os
import sys

# Ensure local directory is in path for imports
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'voik_monochrome_premium_secret_key_2026')

# Session keys:
# - user_id: ID of the logged in user
# - user_name: Name of the logged in user
# - user_role: Role of the logged in user (admin/cliente)
# - light_mode: True (Light) or False (Dark)
# - cart: dict mapping product_id (str) to quantity (int)

@app.before_request
def init_session():
    if 'light_mode' not in session:
        session['light_mode'] = True
    if 'cart' not in session:
        session['cart'] = {}

# --- VIEW ROUTES ---

@app.route('/')
@app.route('/galeria')
def galeria():
    db = SessionLocal()
    try:
        productos = db.query(Producto).all()
        return render_template('galeria.html', productos=productos)
    finally:
        db.close()

@app.route('/nuevo')
def nuevo():
    db = SessionLocal()
    try:
        productos = db.query(Producto).all()
        # Reversing the last 3 products to match the Streamlit "recent launches" behavior
        nuevos = reversed(productos[-3:]) if len(productos) > 0 else []
        return render_template('nuevo.html', productos=nuevos)
    finally:
        db.close()

@app.route('/tendencias')
def tendencias():
    return render_template('tendencias.html')

@app.route('/carrito')
def carrito():
    if not session.get('user_id'):
        return render_template('carrito.html', cart_items=[], total_price=0)
    
    db = SessionLocal()
    try:
        cart = session.get('cart', {})
        cart_items = []
        total_price = 0
        for prod_id_str, qty in cart.items():
            try:
                prod_id = int(prod_id_str)
                product = db.query(Producto).filter(Producto.id == prod_id).first()
                if product:
                    item_total = product.precio * qty
                    total_price += item_total
                    cart_items.append({
                        'id': product.id,
                        'nombre': product.nombre,
                        'precio': product.precio,
                        'qty': qty
                    })
            except ValueError:
                continue
        return render_template('carrito.html', cart_items=cart_items, total_price=total_price)
    finally:
        db.close()

@app.route('/ajustes')
def ajustes():
    return render_template('ajustes.html')

@app.route('/perfil')
def perfil():
    if not session.get('user_id'):
        flash('Debes iniciar sesión para ver tu perfil.', 'warning')
        return redirect(url_for('login'))
    
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == session.get('user_id')).first()
        if not user:
            # Session user not found in DB
            session.clear()
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('login'))
        return render_template('perfil.html', user=user)
    finally:
        db.close()

# --- AUTH ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor complete todos los campos.', 'warning')
            return redirect(url_for('login'))
        
        db = SessionLocal()
        try:
            # Query by username or email
            user = db.query(Usuario).filter(
                (Usuario.nombre_usuario == username) | (Usuario.email == username)
            ).first()
            
            if user and user.activo and verify_password(user.clave.strip(), password.strip()):
                session['user_id'] = user.id
                session['user_name'] = user.nombre
                session['user_role'] = user.rol
                session['cart'] = {} # Initialize empty cart on login
                flash(f'¡Bienvenido {user.nombre}! Iniciaste sesión exitosamente.', 'success')
                return redirect(url_for('galeria'))
            else:
                flash('Usuario o contraseña incorrectos, o cuenta inactiva.', 'danger')
                return redirect(url_for('login'))
        finally:
            db.close()
            
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not nombre or not email or not username or not password:
            flash('Por favor completa todos los campos.', 'warning')
            return redirect(url_for('registro'))
        
        db = SessionLocal()
        try:
            # Check if user already exists
            user_exist = db.query(Usuario).filter(
                (Usuario.nombre_usuario == username) | (Usuario.email == email)
            ).first()
            
            if user_exist:
                flash('El usuario o el correo electrónico ya están registrados.', 'danger')
                return redirect(url_for('registro'))
            
            new_user = Usuario(
                nombre=nombre,
                nombre_usuario=username,
                email=email,
                clave=hash_password(password),
                rol='cliente'
            )
            db.add(new_user)
            db.commit()
            flash('Cuenta creada exitosamente. Ahora puedes Iniciar Sesión.', 'success')
            return redirect(url_for('login'))
        finally:
            db.close()
            
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('galeria'))

# --- CART ACTIONS ---

@app.route('/comprar/<int:product_id>', methods=['POST'])
def comprar_producto(product_id):
    if not session.get('user_id'):
        flash('Debes iniciar sesión para agregar productos al carrito.', 'warning')
        return redirect(url_for('login'))
    
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    session['cart'] = cart
    session.modified = True
    
    flash('Producto añadido a tu bolsa.', 'success')
    return redirect(url_for('carrito'))

@app.route('/eliminar_carrito/<int:product_id>', methods=['POST'])
def eliminar_carrito(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        session.modified = True
        flash('Producto eliminado de tu bolsa.', 'info')
    return redirect(url_for('carrito'))

@app.route('/checkout_carrito', methods=['POST'])
def checkout_carrito():
    session['cart'] = {}
    session.modified = True
    flash('¡Compra realizada con éxito! Tu bolsa ha sido procesada.', 'success')
    return redirect(url_for('carrito'))

# --- PROFILE ACTIONS ---

@app.route('/perfil/add_phone', methods=['POST'])
def perfil_add_phone():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    phone = request.form.get('phone')
    if phone:
        # Mock action: simply flash success
        flash('✅ Teléfono agregado correctamente.', 'success')
    else:
        flash('Por favor ingresa un número de teléfono válido.', 'warning')
        
    return redirect(url_for('perfil', tab='PagarRapido'))

@app.route('/perfil/change_password', methods=['POST'])
def perfil_change_password():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    current_pwd = request.form.get('current_pwd')
    new_pwd = request.form.get('new_pwd')
    confirm_pwd = request.form.get('confirm_pwd')
    
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == session.get('user_id')).first()
        if not user:
            return redirect(url_for('login'))
        
        if not verify_password(user.clave, current_pwd):
            flash('❌ Contraseña actual incorrecta.', 'danger')
            return redirect(url_for('perfil', tab='Configuracion'))
        
        if new_pwd != confirm_pwd:
            flash('❌ Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('perfil', tab='Configuracion'))
            
        if len(new_pwd) < 6:
            flash('❌ La contraseña debe tener al menos 6 caracteres.', 'danger')
            return redirect(url_for('perfil', tab='Configuracion'))
            
        user.clave = hash_password(new_pwd)
        db.commit()
        
        session.clear()
        flash('✅ Contraseña actualizada correctamente. Inicia sesión de nuevo.', 'success')
        return redirect(url_for('login'))
    finally:
        db.close()

# --- ADMIN PANEL ---

@app.route('/admin')
def admin():
    if session.get('user_role') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('galeria'))
    
    db = SessionLocal()
    try:
        productos = db.query(Producto).all()
        return render_template('admin.html', productos=productos)
    finally:
        db.close()

@app.route('/admin/agregar', methods=['POST'])
def admin_agregar_producto():
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))
        
    nombre = request.form.get('prod_nombre')
    precio_str = request.form.get('prod_precio')
    existencia_str = request.form.get('prod_existencia')
    
    if not nombre or not precio_str or not existencia_str:
        flash('Todos los campos son obligatorios.', 'warning')
        return redirect(url_for('admin'))
        
    try:
        precio = float(precio_str)
        existencia = int(existencia_str)
        
        db = SessionLocal()
        nuevo_prod = Producto(nombre=nombre, precio=precio, existencia=existencia)
        db.add(nuevo_prod)
        db.commit()
        flash(f"Producto '{nombre}' agregado correctamente.", 'success')
    except Exception as e:
        flash(f"Error al agregar producto: {str(e)}", 'danger')
    finally:
        db.close()
        
    return redirect(url_for('admin'))

@app.route('/admin/eliminar', methods=['POST'])
def admin_eliminar_producto():
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))
        
    id_to_delete = request.form.get('id_to_delete')
    if not id_to_delete:
        flash('Seleccione un producto para eliminar.', 'warning')
        return redirect(url_for('admin'))
        
    db = SessionLocal()
    try:
        prod_del = db.query(Producto).filter(Producto.id == int(id_to_delete)).first()
        if prod_del:
            db.delete(prod_del)
            db.commit()
            flash('Producto eliminado.', 'success')
        else:
            flash('Producto no encontrado.', 'danger')
    except Exception as e:
        flash(f"Error al eliminar producto: {str(e)}", 'danger')
    finally:
        db.close()
        
    return redirect(url_for('admin'))

# --- API THEME TOGGLE ---

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    # Toggle theme preference
    session['light_mode'] = not session.get('light_mode', True)
    session.modified = True
    return jsonify({'status': 'ok', 'light_mode': session['light_mode']})

def auto_populate_db():
    db = SessionLocal()
    try:
        # Check if products already exist
        count = db.query(Producto).count()
        if count == 0:
            products = [
                Producto(nombre='Auriculares Obsidiana', precio=150000.0, existencia=15),
                Producto(nombre='Teclado Mecánico Obsidiana', precio=220000.0, existencia=10),
                Producto(nombre='Ratón Ergonómico Obsidiana', precio=95000.0, existencia=20),
                Producto(nombre='Monitor Curvo Obsidiana 27"', precio=650000.0, existencia=5),
                Producto(nombre='Alfombrilla Gamer XL', precio=45000.0, existencia=30),
                Producto(nombre='Soporte Auriculares Alum', precio=60000.0, existencia=12)
            ]
            db.bulk_save_objects(products)
            db.commit()
            print("Database populated with 6 mock products.")
        
        # Check if admin user exists
        admin_count = db.query(Usuario).filter(Usuario.nombre_usuario == 'admin').count()
        if admin_count == 0:
            admin_user = Usuario(
                nombre='Administrador',
                nombre_usuario='admin',
                email='admin@voik.com',
                clave='admin123',
                activo=True,
                rol='admin'
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created: admin / admin123")
    except Exception as e:
        print(f"Error auto-populating database: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    auto_populate_db()
    # Running Flask app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
