# VOIK — Empresa Software PROM 2026

## ▶️ Cómo correr el proyecto

La versión activa del proyecto se ejecuta con **Flask** desde la carpeta `_legacy/`.

### Pasos para iniciar:

```bash
cd _legacy
python app.py
```

La app abrirá en: **http://localhost:5000** (o el puerto configurado por Flask)

---

## 📁 Estructura del proyecto

```
Empresa_Software_PROM_2026/
│
├── _legacy/                ← App Flask activa y archivos de soporte
│   ├── app.py              ← Punto de entrada Flask (Servidor principal)
│   ├── app_streamlit.py    ← Legacy Streamlit (Desactivado)
│   ├── database.py         ← Conexión y utilidades de base de datos (con fallback a SQLite)
│   ├── models.py           ← Modelos de datos de SQLAlchemy
│   ├── auth.py             ← Autenticación y hashing de contraseñas
│   ├── templates/          ← Plantillas Jinja2 para Flask
│   ├── static/             ← Recursos estáticos (css, imagenes, js)
│   └── .streamlit/         ← Configuración legacy
│
└── README.md               ← Documentación del proyecto
```

---

## 📝 Notas

- El host principal se migró de Streamlit a Flask para mejorar el control del frontend y el rendimiento.
- La base de datos tiene un mecanismo de contingencia: si el servidor MySQL local no está activo, utilizará automáticamente SQLite local (`database.db`).
- Se utiliza el archivo `static/css/voik.css` para el diseño monocromático premium con soporte de temas claro/oscuro.
