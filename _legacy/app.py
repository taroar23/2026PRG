from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from database import SessionLocal, get_db
from models import Usuario, Producto, Compra, DetalleCompra
from auth import hash_password, verify_password
import os
import sys
import base64
import datetime

# PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from io import BytesIO
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ reportlab no instalado. PDFs deshabilitados. Instala con: pip install reportlab")


base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'voik_monochrome_premium_secret_key_2026')


def find_image_for_name(name):
    images_dir = os.path.join(base_dir, 'static', 'imagenes')
    try:
        files = os.listdir(images_dir)
    except Exception:
        return 'image.svg.svg'

    def norm(s):
        return s.replace('"', '').replace("'", '').strip()

    name_clean = norm(name)

    for f in files:
        if f.lower() == (name_clean + '.jpg').lower() or f.lower() == (name_clean + '.png').lower():
            return f

    variants = [
        name_clean,
        name_clean.replace(' ', '_'),
        name_clean.lower(),
        name_clean.replace(' ', '_').lower()
    ]
    for v in variants:
        for f in files:
            if f.lower() == (v + '.jpg').lower() or f.lower() == (v + '.png').lower():
                return f

    name_words = [w.lower() for w in name_clean.split() if len(w) > 1]
    best = (None, 0)
    for f in files:
        fl = f.lower()
        score = sum(1 for w in name_words if w in fl)
        if score > best[1]:
            best = (f, score)

    if best[0] and best[1] > 0:
        return best[0]

    return 'image.svg.svg'


# ─── PDF HELPERS ──────────────────────────────────────────────────────────────

def build_pdf_compras(compras_list, titulo="Reporte de Compras"):
    """Genera PDF con la lista de compras."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch,
                            leftMargin=0.8*inch, rightMargin=0.8*inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('VoikTitle', parent=styles['Title'],
                                 fontSize=22, textColor=colors.HexColor('#121315'),
                                 spaceAfter=6, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('VoikSub', parent=styles['Normal'],
                               fontSize=10, textColor=colors.HexColor('#666666'),
                               spaceAfter=20)

    story.append(Paragraph("VOIK", title_style))
    story.append(Paragraph(titulo, sub_style))
    story.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 12))

    headers = ["ID Compra", "Usuario", "Email", "Fecha", "Total", "Estado", "Productos"]
    data = [headers]
    for c in compras_list:
        productos_str = ", ".join([f"{d.nombre_producto} x{d.cantidad}" for d in c.detalles])
        data.append([
            str(c.id),
            c.usuario.nombre if c.usuario else "—",
            c.usuario.email if c.usuario else "—",
            c.fecha.strftime('%d/%m/%Y %H:%M') if c.fecha else "—",
            f"${c.total:,.0f}",
            c.estado,
            productos_str[:60] + ("..." if len(productos_str) > 60 else "")
        ])

    t = Table(data, colWidths=[0.7*inch, 1.1*inch, 1.5*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1.8*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#121315')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer


def build_pdf_usuarios(usuarios_list):
    """Genera PDF con la lista de usuarios."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch,
                            leftMargin=0.8*inch, rightMargin=0.8*inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('VoikTitle', parent=styles['Title'],
                                 fontSize=22, textColor=colors.HexColor('#121315'),
                                 spaceAfter=6, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('VoikSub', parent=styles['Normal'],
                               fontSize=10, textColor=colors.HexColor('#666666'), spaceAfter=20)

    story.append(Paragraph("VOIK", title_style))
    story.append(Paragraph("Reporte de Usuarios", sub_style))
    story.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 12))

    headers = ["ID", "Nombre", "Usuario", "Email", "Rol", "Activo", "Compras", "Total gastado"]
    data = [headers]
    for u in usuarios_list:
        total_compras = len(u.compras)
        total_gastado = sum(c.total for c in u.compras)
        data.append([
            str(u.id),
            u.nombre,
            u.nombre_usuario,
            u.email,
            u.rol,
            "Sí" if u.activo else "No",
            str(total_compras),
            f"${total_gastado:,.0f}"
        ])

    t = Table(data, colWidths=[0.4*inch, 1.2*inch, 1.0*inch, 1.6*inch, 0.7*inch, 0.5*inch, 0.6*inch, 1.1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#121315')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer


def build_pdf_productos(productos_list):
    """Genera PDF con la lista de productos."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch,
                            leftMargin=0.8*inch, rightMargin=0.8*inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('VoikTitle', parent=styles['Title'],
                                 fontSize=22, textColor=colors.HexColor('#121315'),
                                 spaceAfter=6, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('VoikSub', parent=styles['Normal'],
                               fontSize=10, textColor=colors.HexColor('#666666'), spaceAfter=20)

    story.append(Paragraph("VOIK", title_style))
    story.append(Paragraph("Reporte de Productos", sub_style))
    story.append(Paragraph(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 12))

    headers = ["ID", "Nombre", "Precio", "Existencia", "Unidades vendidas", "Ingresos generados"]
    data = [headers]
    for p in productos_list:
        unidades = sum(d.cantidad for d in p.detalles)
        ingresos = sum(d.subtotal for d in p.detalles)
        data.append([
            str(p.id),
            p.nombre,
            f"${p.precio:,.0f}",
            str(p.existencia),
            str(unidades),
            f"${ingresos:,.0f}"
        ])

    t = Table(data, colWidths=[0.5*inch, 2.5*inch, 1.0*inch, 1.0*inch, 1.2*inch, 1.4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#121315')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer


# ─── SESSION INIT ─────────────────────────────────────────────────────────────

@app.before_request
def init_session():
    if 'light_mode' not in session:
        session['light_mode'] = True
    if 'cart' not in session:
        session['cart'] = {}


# ─── PÁGINAS PRINCIPALES ──────────────────────────────────────────────────────

@app.route('/')
@app.route('/galeria')
def galeria():
    db = SessionLocal()
    try:
        productos_raw = db.query(Producto).all()
        productos = []
        for p in productos_raw:
            img = find_image_for_name(p.nombre)
            productos.append({'id': p.id, 'nombre': p.nombre, 'precio': p.precio, 'imagen': img})
        return render_template('galeria.html', productos=productos)
    finally:
        db.close()

@app.route('/nuevo')
def nuevo():
    db = SessionLocal()
    try:
        productos_raw = db.query(Producto).all()
        productos = []
        for p in productos_raw:
            img = find_image_for_name(p.nombre)
            productos.append({'id': p.id, 'nombre': p.nombre, 'precio': p.precio, 'imagen': img})

        nuevos = list(reversed(productos[-3:])) if len(productos) > 0 else []
        return render_template('nuevo.html', productos=nuevos)
    finally:
        db.close()

@app.route('/tendencias')
def tendencias():
    db = SessionLocal()
    try:
        productos = []
        for p in db.query(Producto).all():
            productos.append({'id': p.id, 'nombre': p.nombre, 'precio': p.precio, 'imagen': find_image_for_name(p.nombre)})
        return render_template('tendencias.html', productos=productos)
    finally:
        db.close()

@app.route('/producto/<int:product_id>')
def detalle_producto(product_id):
    db = SessionLocal()
    try:
        producto = db.query(Producto).filter(Producto.id == product_id).first()
        if not producto:
            flash('Producto no encontrado.', 'warning')
            return redirect(url_for('galeria'))

        return render_template('producto.html', producto={
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'existencia': producto.existencia,
            'imagen': find_image_for_name(producto.nombre)
        })
    finally:
        db.close()

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
            session.clear()
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('login'))
        
        # Obtener historial de compras del usuario
        compras = db.query(Compra).filter(Compra.usuario_id == user.id).order_by(Compra.fecha.desc()).all()
        compras_data = []
        for c in compras:
            detalles = []
            for d in c.detalles:
                detalles.append({
                    'nombre': d.nombre_producto,
                    'precio': d.precio_unitario,
                    'cantidad': d.cantidad,
                    'subtotal': d.subtotal
                })
            compras_data.append({
                'id': c.id,
                'fecha': c.fecha.strftime('%d/%m/%Y %H:%M') if c.fecha else '—',
                'total': c.total,
                'estado': c.estado,
                'detalles': detalles
            })
        
        return render_template('perfil.html', user=user, compras=compras_data)
    finally:
        db.close()


# ─── AUTH ─────────────────────────────────────────────────────────────────────

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
            user = db.query(Usuario).filter(
                (Usuario.nombre_usuario == username) | (Usuario.email == username)
            ).first()
            
            if user and user.activo and verify_password(user.clave.strip(), password.strip()):
                session['user_id'] = user.id
                session['user_name'] = user.nombre
                session['user_role'] = user.rol
                session['cart'] = {}
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


# ─── CARRITO Y COMPRAS ────────────────────────────────────────────────────────

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
    """Procesa la compra y la guarda en la base de datos (visible en PhpMyAdmin)."""
    if not session.get('user_id'):
        flash('Debes iniciar sesión para realizar una compra.', 'warning')
        return redirect(url_for('login'))

    cart = session.get('cart', {})
    if not cart:
        flash('Tu bolsa está vacía.', 'warning')
        return redirect(url_for('carrito'))

    db = SessionLocal()
    try:
        cart_items = []
        total_price = 0.0

        for prod_id_str, qty in cart.items():
            try:
                prod_id = int(prod_id_str)
                product = db.query(Producto).filter(Producto.id == prod_id).first()
                if product:
                    subtotal = product.precio * qty
                    total_price += subtotal
                    cart_items.append({
                        'producto': product,
                        'qty': qty,
                        'subtotal': subtotal
                    })
            except ValueError:
                continue

        if not cart_items:
            flash('No se encontraron productos válidos en tu bolsa.', 'warning')
            return redirect(url_for('carrito'))

        # Crear registro de compra en la BD
        nueva_compra = Compra(
            usuario_id=session['user_id'],
            fecha=datetime.datetime.utcnow(),
            total=total_price,
            estado='completada'
        )
        db.add(nueva_compra)
        db.flush()  # obtener el ID

        # Crear detalles de compra
        for item in cart_items:
            detalle = DetalleCompra(
                compra_id=nueva_compra.id,
                producto_id=item['producto'].id,
                nombre_producto=item['producto'].nombre,
                precio_unitario=item['producto'].precio,
                cantidad=item['qty'],
                subtotal=item['subtotal']
            )
            db.add(detalle)

        db.commit()

        session['cart'] = {}
        session.modified = True
        flash(f'¡Compra #{nueva_compra.id} realizada con éxito! Total: ${total_price:,.0f}. Tu bolsa ha sido procesada.', 'success')
        return redirect(url_for('carrito'))

    except Exception as e:
        db.rollback()
        flash(f'Error al procesar la compra: {str(e)}', 'danger')
        return redirect(url_for('carrito'))
    finally:
        db.close()


# ─── PERFIL ───────────────────────────────────────────────────────────────────

@app.route('/perfil/add_phone', methods=['POST'])
def perfil_add_phone():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    phone = request.form.get('phone')
    if phone:
        flash('Teléfono agregado correctamente.', 'success')
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
            flash('Contraseña actual incorrecta.', 'danger')
            return redirect(url_for('perfil', tab='Configuracion'))
        
        if new_pwd != confirm_pwd:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('perfil', tab='Configuracion'))
            
        if len(new_pwd) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return redirect(url_for('perfil', tab='Configuracion'))
            
        user.clave = hash_password(new_pwd)
        db.commit()
        
        session.clear()
        flash('Contraseña actualizada correctamente. Inicia sesión de nuevo.', 'success')
        return redirect(url_for('login'))
    finally:
        db.close()

@app.route('/perfil/update_info', methods=['POST'])
def perfil_update_info():
    """Actualiza nombre, correo y/o nombre de usuario del perfil."""
    if not session.get('user_id'):
        return redirect(url_for('login'))

    nuevo_nombre = request.form.get('nuevo_nombre', '').strip()
    nuevo_email = request.form.get('nuevo_email', '').strip()
    nuevo_username = request.form.get('nuevo_username', '').strip()

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == session.get('user_id')).first()
        if not user:
            return redirect(url_for('login'))

        if nuevo_nombre:
            user.nombre = nuevo_nombre
            session['user_name'] = nuevo_nombre

        if nuevo_email and nuevo_email != user.email:
            exists = db.query(Usuario).filter(Usuario.email == nuevo_email, Usuario.id != user.id).first()
            if exists:
                flash('Ese correo ya está en uso por otra cuenta.', 'danger')
                return redirect(url_for('perfil', tab='Configuracion'))
            user.email = nuevo_email

        if nuevo_username and nuevo_username != user.nombre_usuario:
            exists = db.query(Usuario).filter(Usuario.nombre_usuario == nuevo_username, Usuario.id != user.id).first()
            if exists:
                flash('Ese nombre de usuario ya está en uso.', 'danger')
                return redirect(url_for('perfil', tab='Configuracion'))
            user.nombre_usuario = nuevo_username

        db.commit()
        flash('Información actualizada correctamente.', 'success')
        return redirect(url_for('perfil', tab='Configuracion'))
    finally:
        db.close()

@app.route('/perfil/update_photo', methods=['POST'])
def perfil_update_photo():
    """Actualiza la foto de perfil (base64)."""
    if not session.get('user_id'):
        return redirect(url_for('login'))

    foto = request.files.get('foto_perfil')
    if not foto or foto.filename == '':
        flash('No se seleccionó ninguna imagen.', 'warning')
        return redirect(url_for('perfil', tab='Configuracion'))

    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = foto.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        flash('Formato de imagen no permitido. Usa PNG, JPG o GIF.', 'danger')
        return redirect(url_for('perfil', tab='Configuracion'))

    foto_data = foto.read()
    if len(foto_data) > 2 * 1024 * 1024:  # 2MB limit
        flash('La imagen es demasiado grande. Máximo 2MB.', 'danger')
        return redirect(url_for('perfil', tab='Configuracion'))

    foto_b64 = f"data:image/{ext};base64,{base64.b64encode(foto_data).decode()}"

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == session.get('user_id')).first()
        if user:
            user.foto_perfil = foto_b64
            db.commit()
            flash('Foto de perfil actualizada.', 'success')
    finally:
        db.close()

    return redirect(url_for('perfil', tab='Configuracion'))


# ─── PDF PERFIL (historial personal) ──────────────────────────────────────────

@app.route('/perfil/pdf_historial')
def perfil_pdf_historial():
    """Descarga PDF del historial de compras del usuario logueado."""
    if not session.get('user_id'):
        return redirect(url_for('login'))

    if not PDF_AVAILABLE:
        flash('Generación de PDF no disponible. Instala reportlab.', 'danger')
        return redirect(url_for('perfil', tab='Historial'))

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == session.get('user_id')).first()
        compras = db.query(Compra).filter(Compra.usuario_id == user.id).order_by(Compra.fecha.desc()).all()
        
        buffer = build_pdf_compras(compras, titulo=f"Historial de Compras — {user.nombre}")
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=historial_{user.nombre_usuario}.pdf'
        return response
    finally:
        db.close()


# ─── ADMIN ────────────────────────────────────────────────────────────────────

@app.route('/admin')
def admin():
    if session.get('user_role') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
        return redirect(url_for('galeria'))
    
    db = SessionLocal()
    try:
        productos = db.query(Producto).all()
        usuarios = db.query(Usuario).all()
        compras = db.query(Compra).order_by(Compra.fecha.desc()).all()
        
        # Stats
        total_compras = len(compras)
        total_ingresos = sum(c.total for c in compras)
        total_usuarios = len(usuarios)
        
        # Preparar datos de usuarios con info de compras
        usuarios_data = []
        for u in usuarios:
            usuarios_data.append({
                'id': u.id,
                'nombre': u.nombre,
                'nombre_usuario': u.nombre_usuario,
                'email': u.email,
                'rol': u.rol,
                'activo': u.activo,
                'num_compras': len(u.compras),
                'total_gastado': sum(c.total for c in u.compras)
            })
        
        # Preparar compras con datos del usuario
        compras_data = []
        for c in compras:
            compras_data.append({
                'id': c.id,
                'usuario': c.usuario.nombre if c.usuario else '—',
                'email': c.usuario.email if c.usuario else '—',
                'fecha': c.fecha.strftime('%d/%m/%Y %H:%M') if c.fecha else '—',
                'total': c.total,
                'estado': c.estado,
                'detalles': [{'nombre': d.nombre_producto, 'cantidad': d.cantidad, 'subtotal': d.subtotal} for d in c.detalles]
            })

        return render_template('admin.html',
                               productos=productos,
                               usuarios=usuarios_data,
                               compras=compras_data,
                               stats={
                                   'total_compras': total_compras,
                                   'total_ingresos': total_ingresos,
                                   'total_usuarios': total_usuarios,
                                   'total_productos': len(productos)
                               })
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

@app.route('/admin/usuario/cambiar_rol', methods=['POST'])
def admin_cambiar_rol():
    """Permite al admin cambiar el rol de un usuario."""
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))

    usuario_id = request.form.get('usuario_id')
    nuevo_rol = request.form.get('nuevo_rol')

    if not usuario_id or nuevo_rol not in ('admin', 'cliente', 'moderador'):
        flash('Datos inválidos.', 'danger')
        return redirect(url_for('admin') + '#usuarios')

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
        if user:
            user.rol = nuevo_rol
            db.commit()
            flash(f"Rol de '{user.nombre}' cambiado a '{nuevo_rol}'.", 'success')
        else:
            flash('Usuario no encontrado.', 'danger')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
    finally:
        db.close()

    return redirect(url_for('admin') + '#usuarios')

@app.route('/admin/usuario/toggle_activo', methods=['POST'])
def admin_toggle_activo():
    """Activa o desactiva un usuario."""
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))

    usuario_id = request.form.get('usuario_id')
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
        if user:
            user.activo = not user.activo
            estado = "activado" if user.activo else "desactivado"
            db.commit()
            flash(f"Usuario '{user.nombre}' {estado}.", 'success')
        else:
            flash('Usuario no encontrado.', 'danger')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
    finally:
        db.close()

    return redirect(url_for('admin') + '#usuarios')

@app.route('/admin/usuario/eliminar', methods=['POST'])
def admin_eliminar_usuario():
    """Elimina un usuario y sus compras asociadas."""
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))

    usuario_id = request.form.get('usuario_id')
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
        if user:
            if user.id == session.get('user_id'):
                flash('No puedes eliminar tu propia cuenta de admin.', 'danger')
                return redirect(url_for('admin') + '#usuarios')
            nombre = user.nombre
            # Eliminar detalles de compra primero
            for compra in user.compras:
                for detalle in compra.detalles:
                    db.delete(detalle)
                db.delete(compra)
            db.delete(user)
            db.commit()
            flash(f"Usuario '{nombre}' eliminado correctamente.", 'success')
        else:
            flash('Usuario no encontrado.', 'danger')
    except Exception as e:
        db.rollback()
        flash(f"Error: {str(e)}", 'danger')
    finally:
        db.close()

    return redirect(url_for('admin') + '#usuarios')


# ─── PDFs ADMIN ───────────────────────────────────────────────────────────────

@app.route('/admin/pdf/compras')
def admin_pdf_compras():
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))
    if not PDF_AVAILABLE:
        flash('reportlab no instalado. Ejecuta: pip install reportlab', 'danger')
        return redirect(url_for('admin'))

    db = SessionLocal()
    try:
        compras = db.query(Compra).order_by(Compra.fecha.desc()).all()
        buffer = build_pdf_compras(compras, "Reporte de Todas las Compras")
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_compras.pdf'
        return response
    finally:
        db.close()

@app.route('/admin/pdf/usuarios')
def admin_pdf_usuarios():
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))
    if not PDF_AVAILABLE:
        flash('reportlab no instalado. Ejecuta: pip install reportlab', 'danger')
        return redirect(url_for('admin'))

    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        buffer = build_pdf_usuarios(usuarios)
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_usuarios.pdf'
        return response
    finally:
        db.close()

@app.route('/admin/pdf/productos')
def admin_pdf_productos():
    if session.get('user_role') != 'admin':
        return redirect(url_for('galeria'))
    if not PDF_AVAILABLE:
        flash('reportlab no instalado. Ejecuta: pip install reportlab', 'danger')
        return redirect(url_for('admin'))

    db = SessionLocal()
    try:
        productos = db.query(Producto).all()
        buffer = build_pdf_productos(productos)
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_productos.pdf'
        return response
    finally:
        db.close()


# ─── THEME ────────────────────────────────────────────────────────────────────

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    session['light_mode'] = not session.get('light_mode', True)
    session.modified = True
    return jsonify({'status': 'ok', 'light_mode': session['light_mode']})


# ─── AUTO-POPULATE ────────────────────────────────────────────────────────────

def auto_populate_db():
    db = SessionLocal()
    try:
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
    app.run(host='0.0.0.0', port=5000, debug=True)
