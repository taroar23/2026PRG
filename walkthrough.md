# VOIK — Documentación Técnica de Sustentación

## 1. Descripción General del Proyecto

**VOIK** es una aplicación web de comercio electrónico de estética minimalista monocromática.
Fue migrada desde **Streamlit** (un framework de prototipado rápido en Python) hacia **Flask**
(un framework web de producción), con el objetivo de tener control total sobre el frontend,
las rutas HTTP, la lógica de sesiones y la presentación visual.

### Stack Tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| Backend | Python + Flask 3.1 | Servidor web, rutas, lógica de negocio |
| Base de datos | SQLAlchemy + MySQL / SQLite | ORM para consultas, con fallback automático |
| Frontend | HTML + Jinja2 | Plantillas dinámicas renderizadas en servidor |
| Estilos | CSS puro (voik.css) | Diseño premium, temas claro/oscuro |
| Tipografía | Google Fonts — Inter | Fuente moderna ultra-ligera |

---

## 2. Arquitectura del Proyecto

```
_legacy/
├── app.py               ← Punto de entrada del servidor Flask
├── database.py          ← Conexión a base de datos (MySQL o SQLite)
├── models.py            ← Definición de tablas con SQLAlchemy
├── auth.py              ← Utilidades de autenticación
├── database.db          ← Base de datos SQLite (fallback local)
├── .env                 ← Variables de entorno (credenciales MySQL)
│
├── templates/           ← Páginas HTML renderizadas por Flask (Jinja2)
│   ├── base.html        ← Layout base: navbar, footer, scripts
│   ├── galeria.html     ← Catálogo principal con hero section
│   ├── nuevo.html       ← Últimos 3 productos (lanzamientos)
│   ├── tendencias.html  ← Página de tendencias
│   ├── carrito.html     ← Bolsa de compras del usuario
│   ├── perfil.html      ← Panel de perfil con sub-secciones
│   ├── login.html       ← Formulario de inicio de sesión
│   ├── registro.html    ← Formulario de registro
│   ├── admin.html       ← Panel de administración de productos
│   └── ajustes.html     ← Configuración del sitio
│
└── static/
    ├── css/
    │   └── voik.css     ← Todos los estilos del proyecto
    └── imagenes/        ← Logos, íconos SVG (versiones black)
```

---

## 3. Archivo: `database.py`

**Propósito:** Gestionar la conexión a la base de datos y proveer sesiones a los demás módulos.

### Líneas 1–8 — Carga de configuración
```python
load_dotenv(os.path.join(base_dir, ".env"))
```
Carga las credenciales del archivo `.env` (usuario, contraseña, host, nombre de base de datos MySQL).
Esto evita tener credenciales escritas directamente en el código (buena práctica de seguridad).

### Líneas 10–13 — URI de conexión MySQL
```python
DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```
Construye la cadena de conexión para MySQL usando el driver `PyMySQL`.
El formato es estándar de SQLAlchemy.

### Líneas 15–21 — Fallback automático a SQLite
```python
try:
    engine = create_engine(DATABASE_URI, ...)
    with engine.connect() as conn:
        pass   # prueba real de conexión
except Exception:
    DATABASE_URI = f"sqlite:///{db_path}"
    engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False})
```
**Decisión de diseño clave:** si MySQL no está disponible (servidor apagado, credenciales incorrectas),
el sistema automáticamente usa SQLite local (`database.db`). Esto garantiza que la aplicación
siempre pueda correr en entorno de desarrollo sin configuración externa.

### Líneas 23–30 — Fábrica de sesiones
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```
`SessionLocal` es una "fábrica" que genera sesiones de base de datos bajo demanda.
Cada vista de Flask crea su propia sesión, hace su consulta, y la cierra en el bloque `finally`.
Esto evita fugas de conexiones.

### Líneas 32–33 — Auto-creación de tablas
```python
import models
Base.metadata.create_all(bind=engine)
```
Al importar `models`, registra las clases `Usuario` y `Producto` en el `Base`.
`create_all()` crea las tablas físicamente si no existen, sin borrar datos existentes.

---

## 4. Archivo: `models.py`

**Propósito:** Definir la estructura de las tablas de la base de datos usando clases Python (ORM).

### Líneas 4–16 — Clase `Usuario`
```python
class Usuario(Base):
    __tablename__ = "usuarios"
    id            = Column(Integer, primary_key=True)
    nombre        = Column(String(50))
    nombre_usuario= Column(String(50), unique=True)
    email         = Column(String(120), unique=True)
    clave         = Column(String(200))
    activo        = Column(Boolean, default=True)
    rol           = Column(String(20), default="cliente")
```
Cada atributo de la clase corresponde a una columna en la tabla `usuarios`.
`unique=True` en `nombre_usuario` y `email` previene duplicados a nivel de base de datos.
El campo `activo` permite deshabilitar cuentas sin eliminarlas.
El campo `rol` diferencia entre `"cliente"` y `"admin"`.

### Líneas 18–27 — Clase `Producto`
```python
class Producto(Base):
    __tablename__ = "productos"
    id         = Column(Integer, primary_key=True)
    nombre     = Column(String(100))
    precio     = Column(Float)
    existencia = Column(Integer, default=0)
```
Estructura simple para el catálogo. `existencia` es el stock disponible.

---

## 5. Archivo: `auth.py`

**Propósito:** Centralizar la lógica de manejo de contraseñas.

### Líneas 1–2 — `hash_password(password)`
Actualmente retorna la contraseña sin transformación. En producción esta función
debería usar `bcrypt` o `werkzeug.security.generate_password_hash` para almacenar
hashes seguros en lugar de texto plano.

### Líneas 4–5 — `verify_password(stored, input)`
Compara la contraseña almacenada con la ingresada. Al estar separada en su propio módulo,
si se mejora la seguridad (cambiando a hashing real), solo hay que modificar este archivo
sin tocar el resto de la aplicación.

---

## 6. Archivo: `app.py` — El servidor Flask

**Propósito:** Definir todas las rutas HTTP, procesar formularios, manejar sesiones y renderizar páginas.

### Líneas 1–13 — Configuración inicial
```python
app = Flask(__name__)
app.secret_key = '...'
```
`secret_key` es indispensable para que Flask pueda firmar criptográficamente las cookies de sesión.
Sin él, un atacante podría falsificar sesiones.

### Líneas 22–27 — `init_session()` (before_request)
```python
@app.before_request
def init_session():
    if 'light_mode' not in session: session['light_mode'] = True
    if 'cart' not in session:       session['cart'] = {}
```
Se ejecuta **antes de cada request**. Garantiza que las claves de sesión siempre existan,
evitando errores `KeyError` en las plantillas. El carrito es un diccionario `{product_id: cantidad}`.

---

### Rutas de vista (páginas)

#### Líneas 31–39 — `galeria()` → `GET /`
Página principal. Consulta **todos** los productos de la BD y los pasa al template `galeria.html`.
El template los muestra en un grid de 3 columnas con imagen, nombre, precio y botón de compra.

#### Líneas 41–50 — `nuevo()` → `GET /nuevo`
Toma los últimos 3 productos de la lista y los presenta en sentido inverso (el más nuevo primero).
Simula una sección de "lanzamientos recientes".

#### Líneas 52–54 — `tendencias()` → `GET /tendencias`
Vista estática. Muestra un mensaje informativo indicando que el módulo de análisis está en desarrollo.

#### Líneas 56–83 — `carrito()` → `GET /carrito`
Si el usuario no está autenticado, renderiza el carrito vacío con advertencia.
Si está autenticado, recorre el diccionario de sesión `cart`, consulta cada producto en la BD,
calcula el total acumulado y pasa la lista enriquecida al template.

#### Líneas 89–105 — `perfil()` → `GET /perfil`
Requiere sesión activa (`user_id`). Consulta el usuario actual en la BD.
Si el usuario fue eliminado pero la sesión persiste, limpia la sesión y redirige al login.
El sub-panel se controla con el parámetro URL `?tab=Inicio` (Guardado, Cuotas, etc.).

---

### Rutas de autenticación

#### Líneas 109–139 — `login()` → `GET/POST /login`
**GET:** renderiza el formulario vacío.
**POST:** busca al usuario por `nombre_usuario` O `email` (acepta ambos), verifica contraseña,
verifica que la cuenta esté activa. Si todo es correcto, escribe `user_id`, `user_name` y `user_role`
en la sesión de Flask y redirige a la galería.

#### Líneas 141–178 — `registro()` → `GET/POST /registro`
Verifica que el usuario o email no existan ya en la BD antes de crear la cuenta.
Si hay duplicado, muestra error. Si no, inserta el nuevo usuario con rol `"cliente"`.

#### Líneas 180–184 — `logout()` → `GET /logout`
`session.clear()` elimina **todos** los datos de sesión (usuario, carrito, tema).
Redirige a la galería con mensaje de confirmación.

---

### Rutas del carrito

#### Líneas 188–201 — `comprar_producto(product_id)` → `POST /comprar/<id>`
Solo accesible si hay sesión activa. Incrementa en 1 la cantidad del producto en el diccionario
de sesión. `session.modified = True` es necesario porque Flask no detecta cambios en estructuras
anidadas automáticamente.

#### Líneas 203–212 — `eliminar_carrito(product_id)` → `POST /eliminar_carrito/<id>`
Elimina la entrada del diccionario de sesión si existe. No falla si el producto ya no está.

#### Líneas 214–219 — `checkout_carrito()` → `POST /checkout_carrito`
Vacía el carrito completamente. Simula el procesamiento de pago (en producción aquí iría
la integración con pasarela de pagos como Stripe o PayU).

---

### Rutas del perfil

#### Líneas 223–235 — `perfil_add_phone()` → `POST /perfil/add_phone`
Acción de mock: registra el número de teléfono (en esta versión solo muestra confirmación).
En producción enviaría un SMS de verificación.

#### Líneas 237–271 — `perfil_change_password()` → `POST /perfil/change_password`
Valida 3 condiciones antes de cambiar la contraseña:
1. La contraseña actual es correcta.
2. La nueva contraseña y su confirmación coinciden.
3. La nueva contraseña tiene mínimo 6 caracteres.

Si pasa todo, actualiza en BD y cierra la sesión (el usuario debe re-autenticarse).

---

### Panel de administración

#### Líneas 275–286 — `admin()` → `GET /admin`
Verifica que `session['user_role'] == 'admin'`. Si no, deniega el acceso.
Lista todos los productos de la BD.

#### Líneas 288–315 — `admin_agregar_producto()` → `POST /admin/agregar`
Valida que todos los campos estén presentes, convierte precio a `float` y existencia a `int`,
inserta el nuevo producto en la BD.

#### Líneas 317–341 — `admin_eliminar_producto()` → `POST /admin/eliminar`
Busca el producto por ID, lo elimina de la BD con `db.delete()` y confirma.

---

### API interna

#### Líneas 345–350 — `toggle_theme()` → `POST /toggle-theme`
Invierte el valor booleano `session['light_mode']` y retorna JSON.
No recarga la página — el CSS hace la transición en tiempo real mediante `filter: invert()`.

#### Líneas 352–387 — `auto_populate_db()`
Función que corre una sola vez al iniciar el servidor. Inserta 6 productos de ejemplo y
el usuario administrador (`admin` / `admin123`) si no existen. Garantiza que la app
funcione inmediatamente sin configuración manual.

---

## 7. Archivo: `static/css/voik.css`

**Propósito:** Definir toda la apariencia visual del sitio. Sin librerías externas (CSS puro).

### Líneas 2–30 — Variables de tema claro (`:root`)
Se definen **variables CSS** para cada color del sistema. Usar variables permite cambiar
el tema completo modificando solo este bloque, sin tocar ningún otro selector.

```css
:root {
    --bg-color: #f8f9fa;      /* Fondo principal */
    --text-color: #121315;    /* Texto principal */
    --text-muted: #666666;    /* Texto secundario */
    --card-bg: #ffffff;       /* Fondo de tarjetas */
    --button-primary-bg: #121315; /* Botón de acción principal */
    ...
}
```

### Líneas 32–58 — Variables de tema oscuro (`[data-theme="dark"]`)
Sobreescribe las mismas variables para modo oscuro. Cuando el `<html>` tiene
`data-theme="dark"`, todas las variables cambian automáticamente.

### Líneas 61–69 — Transición global en `*`
```css
* {
    transition: background-color 0.5s, color 0.5s, border-color 0.5s ...
}
```
Aplica transición suave a **todos** los elementos del sitio. Cuando las variables CSS cambian,
el navegador interpola suavemente entre el color anterior y el nuevo durante 0.5 segundos.
La curva `cubic-bezier(0.4, 0, 0.2, 1)` es la curva "ease" de Material Design — se siente natural.

### Líneas 71–83 — Transición de imágenes con `filter`
```css
.logo-img, .profile-menu-item img {
    transition: filter 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-theme="dark"] .logo-img {
    filter: invert(1);
}
```
**Técnica clave:** en lugar de cargar dos versiones de cada ícono (negro y blanco) y recargar
la página al cambiar tema, se usa `filter: invert(1)` que invierte matemáticamente los colores
de la imagen. Negro (`#000`) se vuelve blanco (`#fff`) y viceversa. La transición se anima
suavemente igual que el texto.

### Líneas 127–148 — Logo y brand text
```css
.logo-link { display: inline-flex; align-items: center; gap: 12px; }
.logo-img  { height: 42px; }
.logo-brand-text {
    font-family: 'Inter', sans-serif;
    font-weight: 200;      /* Ultra-ligero: estética premium */
    font-size: 22px;
    letter-spacing: 5px;  /* Espaciado amplio: look de lujo */
}
```
El diseño del logotipo combina la imagen del símbolo con el nombre de la marca en tipografía
Inter weight 200, que es inusualmente delgada y transmite sofisticación minimalista.

---

## 8. Sistema de Plantillas HTML (`templates/`)

Flask usa el motor de plantillas **Jinja2** que permite:
- `{{ variable }}` — insertar valores de Python en HTML
- `{% if %} / {% for %}` — lógica de control
- `{% extends "base.html" %}` — herencia de plantillas
- `{% block content %}` — zonas reemplazables

### `base.html` — El layout maestro
Todas las páginas "heredan" de este archivo. Contiene:
- `<head>` con fuentes, CSS y metadatos
- El `<header>` con logo, navbar, toggle de tema y menú de cuenta
- El `<main>` con `{% block content %}` — zona que cada página rellena
- El `<footer>` con copyright
- El `<script>` con la lógica del toggle de tema y el popover de usuario

### Toggle de tema — Flujo completo
```
Usuario hace click en el switch
    ↓
JavaScript cambia data-theme="dark" en <html> (INMEDIATO)
    ↓
CSS variables cambian → transición de 0.5s en colores e imágenes
    ↓
fetch('/toggle-theme') actualiza session['light_mode'] en el servidor (en background)
    ↓
Al navegar a otra página, el servidor renderiza la plantilla con el tema correcto
```

---

## 9. Flujo de datos completo — Ejemplo: comprar un producto

```
1. Usuario visita GET /
   → galeria() consulta Producto.query.all() en BD
   → Flask renderiza galeria.html con la lista
   → Navegador muestra el grid de productos

2. Usuario hace clic en "🛒 Comprar" en un producto (ID=3)
   → POST /comprar/3

3. comprar_producto(3) en app.py (línea 188):
   → Verifica sesión activa (user_id)
   → session['cart']['3'] += 1
   → Redirige a GET /carrito

4. carrito() en app.py (línea 56):
   → Lee session['cart'] = {'3': 1}
   → Consulta Producto con id=3 en BD
   → Calcula total: precio × cantidad
   → Renderiza carrito.html con la lista

5. Usuario ve su bolsa con el producto y el total
```

---

## 10. Seguridad implementada

| Medida | Dónde | Qué previene |
|---|---|---|
| `app.secret_key` | `app.py` L13 | Falsificación de cookies de sesión |
| Verificación de `user_role` | `app.py` L277 | Acceso no autorizado al panel admin |
| Verificación de `user_id` | `app.py` L58, 91, 190 | Acceso a recursos sin autenticación |
| `unique=True` en BD | `models.py` L9, 10 | Registro duplicado de usuarios |
| Verificación de cuenta activa | `app.py` L126 | Acceso de cuentas deshabilitadas |
| `session.clear()` en logout | `app.py` L182 | Persistencia de sesión tras cierre |

> [!NOTE]
> En la versión actual, las contraseñas se guardan en texto plano en la BD.
> Para producción se recomienda implementar `bcrypt` en `auth.py`.

---

## 11. Cómo ejecutar el proyecto

```bash
# Desde la carpeta _legacy/
python app.py
```

La aplicación:
1. Intenta conectar a MySQL (credenciales en `.env`)
2. Si falla, usa SQLite automáticamente
3. Verifica si hay productos y un admin — los crea si no existen
4. Inicia el servidor en `http://localhost:5000`

**Credenciales de prueba (admin):**
- Usuario: `admin`
- Contraseña: `admin123`
