import streamlit as st
from database import get_db, SessionLocal
from models import Usuario, Producto
from auth import hash_password, verify_password
import time


st.set_page_config(page_title="Voik", page_icon="", layout="wide", initial_sidebar_state="expanded")


import os
from pathlib import Path
base_dir = os.path.abspath(os.path.dirname(__file__))

# Initialize light_mode session state
if 'light_mode' not in st.session_state:
    st.session_state.light_mode = True

# Load logo based on theme mode
logo_filename = 'vk_black.png' if st.session_state.light_mode else 'vk_white.png'
logo_path = os.path.join(base_dir, 'static', 'imagenes', logo_filename)
if os.path.exists(logo_path):
    st.image(logo_path, width=90)



st.markdown("""
    <style>
    
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    
    .block-container {
        padding-top: 1rem !important; 
        max-width: 95%;
        font-family: 'Inter', sans-serif;
        background-color: #121315 !important;
        transition: background-color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #ffffff !important;
    }
    
    .stApp {
        background-color: #121315 !important;
        transition: background-color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    
    [data-testid="stTextInput"] input {
        background-color: #1a1b1e !important;
        border: 1px solid #2a2c30 !important;
        color: white !important;
        border-radius: 4px;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    
    .stButton>button {
        border-radius: 4px;
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold;
        border: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        background-color: #cccccc !important;
        transform: translateY(-2px);
    }
    
    
    div[data-testid="stPopoverBody"] {
        background-color: #121315 !important;
        border: 1px solid #1a1b1e !important;
        color: #ffffff !important;
        padding: 10px 15px !important;
        min-width: 180px !important;
        width: 180px !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    
    div[data-testid="stPopoverBody"] .stButton>button {
        background-color: transparent !important;
        color: #f8f9fa !important;
        border: none !important;
        border-bottom: 1px solid #2a2c30 !important;
        border-radius: 0px !important;
        font-weight: normal !important;
        text-align: left !important;
        padding: 10px 0px !important;
        margin: 0px !important;
        justify-content: flex-start !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stPopoverBody"] .stButton>button:hover {
        background-color: transparent !important;
        color: #ffffff !important;
        border-bottom: 1px solid #ffffff !important;
        padding-left: 8px !important;
    }
    
    
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        color: #a0a0a0 !important;
        border: none !important;
        font-size: 18px !important;
        padding: 0px !important;
        box-shadow: none !important;
        float: right !important;
        margin-top: -4px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stPopover"] > button:hover {
        color: #ffffff !important;
        background-color: transparent !important;
        transform: scale(1.1);
    }
    
    
    .profile-menu-button {
        background-color: transparent !important;
        border: none !important;
        color: #a0a0a0 !important;
        padding: 10px 0px !important;
        text-align: left !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }
    .profile-menu-button:hover {
        color: #ffffff !important;
        padding-left: 8px !important;
    }
    
    
    iframe[title="streamlit_option_menu.option_menu"] {
        margin-top: 0 !important;
        vertical-align: middle !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        min-height: 60px !important;
    }
    
    
    div[data-testid="stToggle"], div[data-testid="stPopover"] > button {
        margin-top: 0 !important;
        padding-top: 0 !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div[data-testid="stFileUploader"] { display: none; }
    
    
    * {
        transition: background-color 0.6s cubic-bezier(0.4, 0, 0.2, 1), 
                    color 0.6s cubic-bezier(0.4, 0, 0.2, 1),
                    border-color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    </style>
""", unsafe_allow_html=True)


if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'light_mode' not in st.session_state:
    st.session_state.light_mode = True

pfp_file = os.path.join(base_dir, "pfpblack.png") if st.session_state.light_mode else os.path.join(base_dir, "pfpwhite.png")
pfp_uri = Path(pfp_file).as_uri()


if st.session_state.light_mode:
    st.markdown("""
        <style>
        @keyframes fadeTransition {
            0% { opacity: 1; }
            50% { opacity: 0.95; }
            100% { opacity: 1; }
        }
        
        
        .stApp, .block-container { 
            background-color: #f8f9fa !important;
            animation: fadeTransition 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        
        [data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input { 
            background-color: #ffffff !important;
            border: 1px solid #dcdcdc !important;
            color: #121315 !important;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        
        div[data-testid="stPopoverBody"], .stPopoverBody, div[role="dialog"] { 
            background-color: #ffffff !important;
            border: 1px solid #dddddd !important;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stPopoverBody"] div, .stPopoverBody div, div[role="dialog"] div { 
            background-color: transparent !important;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stPopoverBody"] button, .stPopoverBody button { 
            background-color: #ffffff !important;
            color: #333333 !important;
            border-bottom: 1px solid #eeeeee !important;
            border-radius: 0 !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stPopoverBody"] button:hover, .stPopoverBody button:hover { 
            background-color: #f0f2f6 !important;
            color: #000000 !important;
        }
        
        
        div.stButton > button { 
            background-color: #eeeeee !important;
            color: #121315 !important;
            border: 1px solid #cccccc !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div.stButton > button:hover { 
            background-color: #dddddd !important;
            transform: translateY(-2px);
        }
        
        
        h1, h2, h3, h4, p, span { 
            color: #121315 !important;
            transition: color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        
        [data-testid="stTooltipContent"], 
        [data-testid="stTooltipContent"] p, 
        [data-testid="stTooltipContent"] span {
            color: #ffffff !important;
            background-color: #1a1b1e !important;
        }
        
        
        .dark-card p, .dark-card span {
            color: #ffffff !important;
        }
        .dark-card p.subtext {
            color: #a0a0a0 !important;
        }
        hr { 
            border-top: 1px solid #cccccc !important;
            transition: border-color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        
        [data-testid="stPopover"] button { 
            background: transparent !important;
            background-color: transparent !important; 
            border: none !important; 
            box-shadow: none !important;
            color: #555555 !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        [data-testid="stPopover"] button:hover { 
            color: #000000 !important;
            background-color: transparent !important;
            transform: scale(1.1);
        }
        
        
        div[data-testid="stWidgetLabel"] p { 
            color: #121315 !important;
            transition: color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        
        iframe { 
            background-color: transparent !important;
        }

        
        div[data-testid="stPopover"] > button {
            background-color: transparent !important;
            background-image: none !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 4px 10px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            color: #555555 !important;
            white-space: nowrap !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            min-width: fit-content !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stPopover"] > button:hover {
            color: #000000 !important;
            background-color: #f0f0f0 !important;
        }
        div[data-testid="stPopover"] > button p {
            white-space: nowrap !important;
            overflow: visible !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <style>
        @keyframes fadeTransition {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.95; }}
            100% {{ opacity: 1; }}
        }}
        
        
        .stApp, .block-container {{
            background-color: #121315 !important;
            animation: fadeTransition 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        
        [data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {{
            background-color: #1a1b1e !important;
            border: 1px solid #2a2c30 !important;
            color: #ffffff !important;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        
        div[data-testid="stPopoverBody"], .stPopoverBody, div[role="dialog"] {{
            background-color: #121315 !important;
            border: 1px solid #1a1b1e !important;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        
        div[data-testid="stPopoverBody"] button, .stPopoverBody button {{
            background-color: #1a1b1e !important;
            color: #f8f9fa !important;
            border-bottom: 1px solid #2a2c30 !important;
            border-radius: 0 !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        
        div[data-testid="stPopoverBody"] button:hover, .stPopoverBody button:hover {{
            background-color: #1f2023 !important;
            color: #ffffff !important;
        }}
        
        h1, h2, h3, h4, p, span {{
            color: #ffffff !important;
            transition: color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        
        hr {{
            border-top: 1px solid #2a2c30 !important;
            transition: border-color 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        
        
        div[data-testid="stPopover"] > button {{
            background-color: transparent !important;
            background-image: none !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 4px 10px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            color: #a0a0a0 !important;
            white-space: nowrap !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            min-width: fit-content !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        div[data-testid="stPopover"] > button:hover {{
            color: #ffffff !important;
            background-color: #2a2c30 !important;
        }}
        div[data-testid="stPopover"] > button p {{
            white-space: nowrap !important;
            overflow: visible !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def login_user(username, password):
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter((Usuario.nombre_usuario == username) | (Usuario.email == username)).first()
        if not user:
            return False
        if user.activo and user.clave.strip() == password.strip():
            st.session_state.user_id = user.id
            st.session_state.user_name = user.nombre
            st.session_state.user_role = user.rol
            return True
        return False
    finally:
        db.close()

def logout_user():
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_role = None

def get_productos():
    db = SessionLocal()
    productos = db.query(Producto).all()
    db.close()
    return productos


def load_svg_icon(filename, light_mode=False, size=20):
    """Carga un icono SVG y retorna el contenido HTML.
    
    Convención de archivos en disco (doble extensión):
      - Fondo OSCURO (light_mode=False): ícono BLANCO  -> 'userwhite.svg.svg'
      - Fondo CLARO  (light_mode=True):  ícono NEGRO   -> 'user.svg.svg'
    """
    base_name = filename  

    if not light_mode:
        
        name_no_ext = base_name.replace('.svg', '')
        disk_filename = f"{name_no_ext}white.svg.svg"
    else:
        
        disk_filename = base_name + ".svg"   

    svg_path = os.path.join(base_dir, "static", "imagenes", disk_filename)

    
    if not os.path.exists(svg_path):
        fallback = base_name + ".svg"
        svg_path = os.path.join(base_dir, "static", "imagenes", fallback)

    if os.path.exists(svg_path):
        try:
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            
            svg_content = svg_content.replace(
                '<svg ', f'<svg style="width:{size}px;height:{size}px;display:block;" '
            )
            return (
                f'<div style="display:inline-flex;width:{size}px;height:{size}px;'
                f'align-items:center;justify-content:center;flex-shrink:0;">'
                f'{svg_content}</div>'
            )
        except Exception:
            return ""
    return ""


ICON_MAP = {
    
    "mi_cuenta": "user.svg",
    "editar_perfil": "user-pen.svg",
    "config_cuenta": "user-cog.svg",
    
    
    "metodos_pago": "credit-card.svg",
    "carrito": "shopping-cart.svg",
    
    
    "favoritos": "heart.svg",
    "galeria": "image.svg",
    
    
    "historial_pedidos": "clipboard-list.svg",
    "envios": "van.svg",
    
    
    "tendencias": "trending-up.svg",
    "productos_nuevos": "badge-plus.svg",
    
    
    "suscripciones": "banknote.svg",
    
    
    "configuracion": "settings.svg",
    "ayuda": "circle-question-mark.svg",
}

def get_icon_with_text(icon_key, text, light_mode=False, size=20):
    """Retorna HTML con icono SVG y texto al lado"""
    if icon_key not in ICON_MAP:
        return f"<div>{text}</div>"
    
    icon_html = load_svg_icon(ICON_MAP[icon_key], light_mode, size)
    return f"""
    <div style='display: flex; align-items: center; gap: 12px;'>
        {icon_html}
        <span style='font-size: 14px;'>{text}</span>
    </div>
    """

from streamlit_option_menu import option_menu


col_logo, col_nav, col_toggle, col_icons = st.columns([1.5, 6.5, 1, 1], vertical_alignment="center")

with col_logo:
    logo_file = os.path.join(base_dir, "static", "imagenes", "vk_black.png") if st.session_state.light_mode else os.path.join(base_dir, "static", "imagenes", "vk_white.png")
    if os.path.exists(logo_file):
        st.image(logo_file, width=90)
    else:
        text_color = "#121315" if st.session_state.light_mode else "#ffffff"
        st.markdown(f"<h3 style='color:{text_color}; margin-top:5px; font-weight:300; letter-spacing:2px;'>VOIK</h3>", unsafe_allow_html=True)

with col_nav:
    menu_options = ["Galería", "Nuevo", "Tendencias"]
    
    
    nav_text_color = "#666" if st.session_state.light_mode else "#a0a0a0"
    nav_active_color = "#000" if st.session_state.light_mode else "#ffffff"
    nav_bg_color = "#f8f9fa" if st.session_state.light_mode else "#121315"

    nav_bg_color = "#f8f9fa" if st.session_state.light_mode else "transparent"
    choice = option_menu(
        menu_title=None, 
        options=menu_options, 
        icons=["", "", ""], 
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"background-color": nav_bg_color, "padding": "0!important", "margin":"0px", "border-radius":"0px"},
            "nav-link": {"font-size": "13px", "color": nav_text_color, "text-align": "left", "margin":"0px", "padding": "0px 15px"},
            "nav-link-selected": {"background-color": "transparent", "color": nav_active_color, "font-weight": "600"},
        }
    )

with col_toggle:
    
    st.toggle("Claro", key="light_mode")

with col_icons:
    with st.popover("👤 Cuenta", help="Tu Cuenta"):
        st.markdown("<p style='font-size:11px; color:#666; margin-bottom:10px; letter-spacing:1px;'>MENÚ</p>", unsafe_allow_html=True)
        if st.session_state.user_id:
            if st.button("Mi Perfil", key="btn_prof"): st.session_state.view_override = "Perfil"
            if st.button("Mi Carrito", key="btn_cart"): st.session_state.view_override = "Carrito"
            if st.button("Ajustes", key="btn_set"): st.session_state.view_override = "Ajustes"
            
            if st.session_state.user_role == "admin":
                if st.button("Panel Admin", key="btn_admin"):
                    st.session_state.view_override = "Panel Admin"
            if st.button("Cerrar Sesión", key="btn_logout"):
                logout_user()
                st.rerun()
        else:
            if st.button("Iniciar Sesión", key="btn_login"): st.session_state.view_override = "Iniciar Sesión"
            if st.button("Registrarse", key="btn_reg"): st.session_state.view_override = "Registrarse"
            if st.button("Mi Carrito", key="btn_cart_out"): st.session_state.view_override = "Carrito"
            if st.button("Ajustes", key="btn_set_out"): st.session_state.view_override = "Ajustes"

st.markdown("<hr style='border-top: 1px solid #2a2c30; margin-top: 5px; margin-bottom: 0px;'>", unsafe_allow_html=True)


view_to_show = st.session_state.get('view_override', choice)

if choice != st.session_state.get('last_choice', ''):
    st.session_state.last_choice = choice
    st.session_state.view_override = choice
    view_to_show = choice

if view_to_show == "Galería":
    
    
    col_text, col_img = st.columns([1, 1.2])
    
    with col_text:
        st.markdown("""
            <div style='padding-top: 80px; padding-left: 20px;'>
                <p style="letter-spacing: 3px; font-size: 10px; color: #888; text-transform: uppercase;">Colección de Invierno 2024</p>
                <h1 style="font-size: 65px; font-family: 'Times New Roman', serif; font-weight: 300; margin-bottom: 0; line-height: 1.1; color: #ffffff;">La Serie</h1>
                <h1 style="font-size: 65px; font-family: 'Times New Roman', serif; margin-top: 0; line-height: 1.1; color: #ffffff;">
                    <i style="font-weight: 600;">Obsidiana</i><span style="font-weight: 300;">Oscura</span>
                </h1>
                <p style="color: #a0a0a0; max-width: 400px; font-size: 14px; margin-top: 20px; margin-bottom: 40px; line-height: 1.6;">
                    Hardware minimalista diseñado para el santuario moderno. Diseños atemporales para la vida contemporánea.
                </p>
                <div style="margin-top: 10px; max-width: 250px;">
                    <button style="width:100%; padding:15px; font-weight:bold; background:white; color:black; border:none; cursor:pointer;">VER COLECCIÓN</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
            
    with col_img:
        st.image("https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?q=80&w=2070&auto=format&fit=crop", use_container_width=True)

    st.markdown("<br><hr style='border-top: 1px solid #2a2c30;'><br>", unsafe_allow_html=True)

    
    st.markdown("<h3 style='margin-bottom: 30px; font-weight:300;'>Catálogo Principal</h3>", unsafe_allow_html=True)
    productos = get_productos()
    
    if len(productos) > 0:
        cols = st.columns(3)
        for idx, prod in enumerate(productos):
            with cols[idx % 3]:
                st.image("https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop", use_container_width=True)
                c_name, c_price = st.columns([3, 1])
                c_name.markdown(f"<p style='font-size:16px; margin-bottom:0;'>{prod.nombre}</p><p style='font-size:11px; color:#888;'>Exclusivo Web</p>", unsafe_allow_html=True)
                c_price.markdown(f"<p style='font-size:14px; font-weight:bold; text-align:right;'>${prod.precio:,.0f}</p>", unsafe_allow_html=True)
                st.button("🛒 Comprar", key=f"comp_{prod.id}", use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No hay productos disponibles actualmente.")

elif view_to_show == "Nuevo":
    
    st.markdown("""
        <div style='padding-top: 60px; padding-bottom: 60px; text-align: center;'>
            <h1 style="font-size: 50px; font-family: 'Times New Roman', serif; font-weight: 300; margin-bottom: 0; color: #ffffff;">Lanzamientos Recientes</h1>
            <p style="color: #a0a0a0; max-width: 600px; margin: 20px auto; font-size: 15px;">Descubre nuestras últimas integraciones a la colección principal. Innovación tecnológica envuelta en siluetas silenciosas.</p>
        </div>
    """, unsafe_allow_html=True)
    
    productos = get_productos()
    if len(productos) > 0:
        nuevos = reversed(productos[-3:]) 
        cols = st.columns(3)
        for idx, prod in enumerate(nuevos):
            with cols[idx % 3]:
                st.image("https://plus.unsplash.com/premium_photo-1681228229983-690a29f9bcfe?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
                c_name, c_price = st.columns([3, 1])
                c_name.markdown(f"<p style='font-size:16px; margin-bottom:0;'>{prod.nombre}</p><p style='font-size:11px; color:#888;'>Lanzamiento Exclusivo</p>", unsafe_allow_html=True)
                c_price.markdown(f"<p style='font-size:14px; font-weight:bold; text-align:right;'>${prod.precio:,.0f}</p>", unsafe_allow_html=True)
                st.button("🛒 Ordenar", key=f"nuevo_{prod.id}", use_container_width=True)
    else:
        st.info("Vuelve pronto para ver la nueva colección.")

elif view_to_show == "Tendencias":
    
    st.markdown("""
        <div style='padding-top: 60px; padding-bottom: 60px; text-align: left; border-bottom: 1px solid #2a2c30;'>
            <p style="letter-spacing: 3px; font-size: 10px; color: #888; text-transform: uppercase;">Los Favoritos del Círculo</p>
            <h1 style="font-size: 50px; font-family: 'Times New Roman', serif; font-weight: 300; margin-bottom: 0; color: #ffffff;">Tendencias Actuales</h1>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    st.info("Nuestros servidores están analizando las interacciones. Los artículos más buscados aparecerán aquí próximamente.")
    
if view_to_show in ["Galería", "Nuevo", "Tendencias"]:
    st.markdown("""
        <br><br><br><br>
        <div style="text-align: center; border-top: 1px solid #2a2c30; padding-top: 50px; padding-bottom: 50px;">
            <p style="color: #666; font-size: 12px; letter-spacing: 2px;">© 2026 VOIK. ESTUDIO DE DISEÑO MONOCROMÁTICO.</p>
        </div>
    """, unsafe_allow_html=True)

elif view_to_show == "Carrito":
    st.markdown("""
        <div style='padding-top: 40px; padding-bottom: 20px; border-bottom: 1px solid #2a2c30;'>
            <h1 style="font-size: 40px; font-weight: 300; margin-bottom: 0; color: #ffffff;">Tu Bolsa 🛍️</h1>
        </div>
        <br>
    """, unsafe_allow_html=True)
    if not st.session_state.user_id:
        st.warning("Debes iniciar sesión usando el ícono de perfil (👤) arriba a la derecha para ver tu bolsa de compras.")
    else:
        st.info("Tu bolsa está vacía. Explora nuestra Colección para añadir productos.")
        if st.button("Explorar Colección", type="primary"):
            st.session_state.view_override = "Galería"
            st.rerun()

elif view_to_show == "Perfil":
    
    if 'profile_menu' not in st.session_state:
        st.session_state.profile_menu = "Inicio"
    
    if not st.session_state.user_id:
        st.warning("Debes registrarte o iniciar sesión para ver tu perfil.")
    else:
        db = SessionLocal()
        user = db.query(Usuario).filter(Usuario.id == st.session_state.user_id).first()
        
        
        st.markdown(f"""
            <div style='text-align: center; padding: 30px 0px 20px 0px; border-bottom: 1px solid #2a2c30;'>
                <div style='display: inline-block; width: 60px; height: 60px; background-color: #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 10px;'>
                    {user.nombre[0].upper()}
                </div>
                <p style='margin: 5px 0; color: #a0a0a0; font-size: 14px;'>{user.email}</p>
            </div>
        """, unsafe_allow_html=True)
        
        
        col_menu, col_space, col_content = st.columns([0.8, 0.1, 2.5], gap="small")
        
        with col_menu:
            
            
            text_col  = "#121315" if st.session_state.light_mode else "#ffffff"
            hover_col = "#000000" if st.session_state.light_mode else "#ffffff"
            st.markdown(f"""
            <style>
            
            div[data-testid="stColumn"]:has(.profile-nav-marker) .stButton > button,
            div[data-testid="column"]:has(.profile-nav-marker) .stButton > button {{
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: transparent !important;
                padding: 0 !important;
                margin-top: -46px !important;
                height: 40px !important;
                min-height: 40px !important;
                width: 100% !important;
                cursor: pointer !important;
                position: relative !important;
                z-index: 10 !important;
            }}
            div[data-testid="stColumn"]:has(.profile-nav-marker) .stButton > button:hover,
            div[data-testid="column"]:has(.profile-nav-marker) .stButton > button:hover {{
                background-color: transparent !important;
                border: none !important;
            }}
            
            div[data-testid="stColumn"]:has(.profile-nav-marker) div[data-testid="stElementContainer"]:has(.stButton),
            div[data-testid="column"]:has(.profile-nav-marker) div[data-testid="stElementContainer"]:has(.stButton) {{
                height: 0px !important;
                min-height: 0px !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            div[data-testid="stColumn"]:has(.profile-nav-marker) [data-testid="stHorizontalBlock"],
            div[data-testid="column"]:has(.profile-nav-marker) [data-testid="stHorizontalBlock"] {{
                position: relative !important;
            }}
            </style>
            <span class="profile-nav-marker" style="display:none;"></span>
            """, unsafe_allow_html=True)

            st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)

            
            menu_items = [
                ("mi_cuenta",        "Mi Cuenta",           "Inicio"),
                ("favoritos",        "Guardado",            "Guardado"),
                ("suscripciones",    "Cuotas",              "Cuotas"),
                ("metodos_pago",     "Suscripciones",       "Suscripciones"),
                ("historial_pedidos","Historial de pedidos","Historial"),
                ("configuracion",    "Configuración",       "Configuracion"),
                ("ayuda",            "Ayuda",               "Ayuda"),
            ]

            for icon_key, label, key in menu_items:
                is_selected = st.session_state.profile_menu == key

                
                if is_selected:
                    item_color = "#121315" if st.session_state.light_mode else "#ffffff"
                    item_weight = "600"
                else:
                    item_color = "#888888"
                    item_weight = "400"

                icon_html = load_svg_icon(ICON_MAP[icon_key], st.session_state.light_mode, size=18)

                
                st.markdown(f"""
                <div style='display:flex; align-items:center; gap:10px;
                            padding:9px 4px; color:{item_color};
                            font-size:14px; font-weight:{item_weight};
                            cursor:pointer; border-radius:6px;'>
                    {icon_html}
                    <span>{label}</span>
                </div>
                """, unsafe_allow_html=True)

                
                if st.button("‎", key=f"menu_{key}", use_container_width=True):
                    st.session_state.profile_menu = key
                    st.rerun()
        
        with col_content:
            
            if st.session_state.profile_menu == "Inicio":
                
                cc_icon = load_svg_icon(ICON_MAP["metodos_pago"], st.session_state.light_mode, size=60)
                st.markdown(f"""
                <div class='dark-card' style='background-color: #1a1b1e; padding: 40px; border-radius: 8px; text-align: center; margin-bottom: 30px;'>
                    <div style='width: 80px; height: 80px; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;'>
                        {cc_icon}
                    </div>
                    <p style='margin: 10px 0; font-size: 18px; font-weight: 600;'>Paga más rápido</p>
                    <p class='subtext' style='margin: 15px 0; font-size: 13px; line-height: 1.5;'>Ingresa y verifica un número de teléfono para pagar más rápido en millones de tiendas</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Agregar teléfono", use_container_width=True, type="primary"):
                    st.session_state.profile_menu = "PagarRapido"
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                
                col_tarj1, col_tarj2 = st.columns(2, gap="large")
                
                
                fav_icon = load_svg_icon(ICON_MAP["favoritos"], st.session_state.light_mode, size=50)
                with col_tarj1:
                    st.markdown(f"""
                    <div class='dark-card' style='background-color: #1a1b1e; padding: 40px; border-radius: 8px; text-align: center; cursor: pointer;'>
                        <div style='width: 60px; height: 60px; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;'>
                            {fav_icon}
                        </div>
                        <p style='margin: 0; font-size: 16px; font-weight: 600;'>Guardado</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Ver guardados", key="quick_guardado", use_container_width=True):
                        st.session_state.profile_menu = "Guardado"
                        st.rerun()
                
                
                van_icon = load_svg_icon(ICON_MAP["envios"], st.session_state.light_mode, size=50)
                with col_tarj2:
                    st.markdown(f"""
                    <div class='dark-card' style='background-color: #1a1b1e; padding: 40px; border-radius: 8px; text-align: center; cursor: pointer;'>
                        <div style='width: 60px; height: 60px; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;'>
                            {van_icon}
                        </div>
                        <p style='margin: 0; font-size: 16px; font-weight: 600;'>Envíos</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div style='opacity: 0; height: 20px;'></div>", unsafe_allow_html=True)
            
            
            elif st.session_state.profile_menu == "Guardado":
                st.markdown("## Productos Guardados")
                st.markdown("---")
                st.info("Aquí aparecerán los productos que hayas marcado como favoritos.")
                st.markdown("Actualmente no tienes productos guardados.")
            
            
            elif st.session_state.profile_menu == "Cuotas":
                st.markdown("## Cuotas")
                st.markdown("---")
                st.info("Sistema de cuotas sin interés y planes de pago.")
                st.markdown("Actualmente no tienes cuotas activas.")
            
            
            elif st.session_state.profile_menu == "Suscripciones":
                st.markdown("## Suscripciones")
                st.markdown("---")
                st.info("Gestiona tus suscripciones y membresías.")
                st.markdown("Actualmente no tienes suscripciones activas.")
            
            
            elif st.session_state.profile_menu == "Historial":
                st.markdown("## Historial de Pedidos")
                st.markdown("---")
                st.info("Aquí aparecerán tus compras anteriores.")
                st.markdown("Actualmente no tienes pedidos registrados.")
            
            
            elif st.session_state.profile_menu == "PagarRapido":
                st.markdown("## Paga Más Rápido")
                st.markdown("---")
                st.markdown("Ingresa y verifica un número de teléfono para pagar más rápido en millones de tiendas.")
                
                st.markdown("""
                <div class='dark-card' style='background-color: #1a1b1e; padding: 30px; border-radius: 8px; text-align: center; margin: 20px 0;'>
                    <div style='font-size: 40px; margin-bottom: 15px;'></div>
                    <p style='margin: 10px 0; font-size: 16px; font-weight: 600;'>Paga más rápido</p>
                    <p class='subtext' style='margin: 10px 0; font-size: 13px;'>Ingresa y verifica un número de teléfono para pagar más rápido en millones de tiendas</p>
                </div>
                """, unsafe_allow_html=True)
                
                phone = st.text_input("Número de Teléfono", placeholder="Ingresa tu número de teléfono")
                if st.button("Agregar teléfono", type="primary", use_container_width=True):
                    st.success("Teléfono agregado correctamente.")
            
            elif st.session_state.profile_menu == "Configuracion":
                st.markdown("## Configuración")
                st.markdown("---")
                
                st.subheader("Cuenta")
                if st.button("Editar Información", use_container_width=True):
                    st.session_state.edit_profile = True
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("Seguridad")
                with st.expander("Cambiar Contraseña"):
                    with st.form("change_password_form"):
                        current_pwd = st.text_input("Contraseña Actual", type="password", key="current_pwd_perfil")
                        new_pwd = st.text_input("Nueva Contraseña", type="password", key="new_pwd_perfil")
                        confirm_pwd = st.text_input("Confirmar Contraseña", type="password", key="confirm_pwd_perfil")
                        
                        if st.form_submit_button("Cambiar Contraseña", type="primary", use_container_width=True):
                            if not verify_password(user.clave, current_pwd):
                                st.error("Contraseña actual incorrecta.")
                            elif new_pwd != confirm_pwd:
                                st.error("Las contraseñas no coinciden.")
                            elif len(new_pwd) < 6:
                                st.error("La contraseña debe tener al menos 6 caracteres.")
                            else:
                                user.clave = hash_password(new_pwd)
                                db.commit()
                                st.success("Contraseña actualizada.")
                                time.sleep(2)
                                logout_user()
                                st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("Sesión")
                if st.button("Cerrar Sesión", type="secondary", use_container_width=True):
                    logout_user()
                    st.success("Sesión cerrada.")
                    st.rerun()
            
            
            elif st.session_state.profile_menu == "Ayuda":
                st.markdown("## Ayuda y Soporte")
                st.markdown("---")
                st.markdown("**Preguntas Frecuentes**")
                with st.expander("¿Cómo cambio mi información personal?"):
                    st.write("Ve a Configuración > Editar Información para actualizar tus datos.")
                with st.expander("¿Cómo agrego un número de teléfono?"):
                    st.write("Ve a Paga más rápido e ingresa tu número de teléfono verificado.")
                with st.expander("¿Cómo cierro mi sesión?"):
                    st.write("Ve a Configuración > Sesión y haz clic en Cerrar Sesión.")
        
        db.close()

elif view_to_show == "Ajustes":
    st.markdown("""
        <div style='padding-top: 40px; padding-bottom: 20px; border-bottom: 1px solid #2a2c30;'>
            <h1 style="font-size: 40px; font-weight: 300; margin-bottom: 0; color: #ffffff;">Ajustes</h1>
        </div>
        <br>
    """, unsafe_allow_html=True)
    st.info("Configuraciones del sitio (Idioma, Notificaciones, etc) irían aquí.")

elif view_to_show == "Iniciar Sesión":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    with col2:
        st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Iniciar Sesión</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit:
                if login_user(username, password):
                    st.success(f"¡Bienvenido {st.session_state.user_name}! Iniciaste sesión exitosamente.")
                    st.balloons()
                    time.sleep(2)
                    st.session_state.view_override = "Galería"
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos, o cuenta inactiva.")

elif view_to_show == "Registrarse":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    with col2:
        st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Crear Cuenta Nueva</h2>", unsafe_allow_html=True)
        with st.form("register_form"):
            nombre = st.text_input("Nombre Completo")
            email = st.text_input("Correo Electrónico")
            username = st.text_input("Nombre de Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Registrarse", use_container_width=True)
            
            if submit:
                if nombre and email and username and password:
                    db = SessionLocal()
                    
                    user_exist = db.query(Usuario).filter((Usuario.nombre_usuario == username) | (Usuario.email == email)).first()
                    if user_exist:
                        st.error("El usuario o el correo electrónico ya están registrados.")
                    else:
                        new_user = Usuario(
                            nombre=nombre,
                            nombre_usuario=username,
                            email=email,
                            clave=password,
                            rol="cliente"
                        )
                        db.add(new_user)
                        db.commit()
                        st.success("Cuenta creada exitosamente. Ahora puedes Iniciar Sesión.")
                    db.close()
                else:
                    st.warning("Por favor completa todos los campos.")

elif view_to_show == "Panel Admin":
    if st.session_state.user_role != "admin":
        st.error("Acceso denegado. Se requieren permisos de administrador.")
    else:
        st.title("Panel de Administración de Productos")
        
        st.subheader("Agregar Nuevo Producto")
        with st.form("add_product_form"):
            prod_nombre = st.text_input("Nombre del Producto")
            prod_precio = st.number_input("Precio ($)", min_value=0.0, format="%.2f")
            prod_existencia = st.number_input("Existencia (Cantidad)", min_value=0, step=1)
            submit_prod = st.form_submit_button("Crear Producto")
            
            if submit_prod:
                db = SessionLocal()
                nuevo_prod = Producto(nombre=prod_nombre, precio=prod_precio, existencia=prod_existencia)
                db.add(nuevo_prod)
                db.commit()
                db.close()
                st.success(f"Producto '{prod_nombre}' agregado correctamente.")
                st.rerun()
                
        st.subheader("Productos Actuales")
        productos = get_productos()
        if len(productos) > 0:
            import pandas as pd
            
            df = pd.DataFrame([{"ID": p.id, "Nombre": p.nombre, "Precio": p.precio, "Existencia": p.existencia} for p in productos])
            st.dataframe(df, use_container_width=True)
            
            
            st.subheader("Eliminar Producto")
            id_to_delete = st.selectbox("Seleccionar Producto a Eliminar", options=[p.id for p in productos], format_func=lambda x: next((p.nombre for p in productos if p.id == x), x))
            if st.button("Eliminar", type="primary"):
                db = SessionLocal()
                prod_del = db.query(Producto).filter(Producto.id == id_to_delete).first()
                if prod_del:
                    db.delete(prod_del)
                    db.commit()
                    st.success("Producto eliminado.")
                    st.rerun()
                db.close()
        else:
            st.info("No hay productos en la base de datos.")

elif choice == "Cerrar Sesión":
    logout_user()
    st.success("Has cerrado sesión.")
    st.rerun()
