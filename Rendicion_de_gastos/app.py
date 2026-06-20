import streamlit as st
from infraestructura.base_datos import RepositorioRendicionFirestore
from aplicacion.flujos import CasoUsoRendicion
from interfaz import rendidor, revision, gerencia, tesoreria

# Configuración inicial de la página
st.set_page_config(page_title="FinTrack Pro", layout="wide")

# Inicialización única del Repositorio de Firebase Firestore y Caso de Uso
repositorio = RepositorioRendicionFirestore()
caso_uso = CasoUsoRendicion(repositorio)

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

# SI NO HAY USUARIO: Aplicamos el CSS exclusivo de la tarjeta de Login
if st.session_state.usuario_autenticado is None:
    st.markdown("""
        <style>
        .stApp { 
            background-image: url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1964&auto=format&fit=crop') !important;
            background-size: cover !important;
            background-position: center !important;
        }
        .stApp::before {
            content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(241, 245, 249, 0.1); backdrop-filter: blur(25px); pointer-events: none;
        }
        header { background-color: rgba(0,0,0,0) !important; }
        [data-testid="stForm"] { border: none !important; padding: 0 !important; }
        
        /* Contenedor global de la Tarjeta del Login */
        [data-testid="stHorizontalBlock"] {
            background-color: light-dark(#ffffff, #212529) !important;
            border-radius: 28px !important;
            box-shadow: 0 30px 60px -12px rgba(15, 23, 42, 0.25) !important;
            max-width: 920px !important;  
            margin: 80px auto !important;
            overflow: hidden !important;
        }
        /* Columna Izquierda (Mensaje de bienvenida con gradiente) */
        [data-testid="stHorizontalBlock"] > div:first-child {
            background: linear-gradient(135deg, #11254c 0%, #1e3a8a 100%) !important;
            padding: 50px !important; color: white !important;
            display: flex !important; flex-direction: column !important; justify-content: center !important;
        }
        
        /* --- COLUMNA DERECHA: APARTADO FINTRACK PRO (GRISÁCEO OSCURO EN DARK MODE) --- */
        [data-testid="stHorizontalBlock"] > div:last-child {
            background-color: light-dark(#ffffff, #212529) !important; 
            padding: 50px !important; 
            display: flex !important; flex-direction: column !important; justify-content: center !important;
        }

        /* Título y Subtítulo dinámicos */
        .login-right-title {
            font-size: 20px !important; font-weight: 800 !important; margin: 0 !important; text-align: center !important;
            color: light-dark(#1e3a8a, #ffffff) !important;
        }
        .login-right-subtitle {
            font-size: 14px !important; text-align: center !important; margin-bottom: 25px !important; margin-top: 4px !important;
            color: light-dark(#64748b, #cbd5e1) !important;
        }

        /* Etiquetas externas sobre los inputs (Nombre de Usuario / Contraseña) */
        [data-testid="stHorizontalBlock"] > div:last-child [data-testid="stWidgetLabel"] p {
            color: light-dark(#0f172a, #ffffff) !important;
        }
        
        /* --- CONFIGURACIÓN DE LOS INPUTS (FONDO NEGRO Y BORDES BLANCOS) --- */
        [data-testid="stHorizontalBlock"] div[data-baseweb="input"] {
            border-radius: 30px !important; 
            border: 2px solid light-dark(#0f172a, #ffffff) !important; 
            background-color: light-dark(#ffffff, #121212) !important; 
            padding: 4px 10px !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stHorizontalBlock"] div[data-baseweb="input"] > div {
            background-color: transparent !important;
        }
        
        [data-testid="stHorizontalBlock"] input {
            color: light-dark(#0f172a, #ffffff) !important; 
            background-color: transparent !important;
        }
        
        [data-testid="stHorizontalBlock"] input::placeholder {
            color: light-dark(#64748b, #94a3b8) !important;
        }

        [data-testid="stHorizontalBlock"] div[data-baseweb="input"] svg {
            fill: light-dark(#0f172a, #ffffff) !important;
        }
        
        /* --- BOTÓN DE LOG IN --- */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: light-dark(#0f172a, #ffffff) !important; 
            color: light-dark(#ffffff, #0f172a) !important; 
            border-radius: 30px !important;
            border: 2px solid light-dark(#0f172a, #ffffff) !important;
            padding: 12px 30px !important; 
            font-weight: 700 !important; 
            width: 100% !important; 
            margin-top: 15px !important;
            transition: all 0.25s ease-in-out !important;
        }
        
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: light-dark(#ffffff, #0f172a) !important;
            color: light-dark(#1e3a8a, #ffffff) !important;
            border-color: light-dark(#1e3a8a, #ffffff) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.markdown('<p style="color:#ffffff; font-size:26px; font-weight:800; margin:0;">Welcome Back!</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#cbd5e1; font-size:14px; margin-top:12px; line-height:1.6;">Plataforma integrada para la carga técnica, validación automatizada y conciliación de gastos corporativos financieros.</p>', unsafe_allow_html=True)
        
    with col_der:
        st.markdown('<p class="login-right-title">FinTrack Pro</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-right-subtitle">Ingresa tus credenciales para continuar</p>', unsafe_allow_html=True)
        
        with st.form("form_login_exact", clear_on_submit=False):
            username = st.text_input("Nombre de Usuario", placeholder="Ej: francisco")
            password = st.text_input("Contraseña corporativa", type="password")
            btn_login = st.form_submit_button("LOG IN")
            
            if btn_login:
                user = repositorio.validar_credenciales(username, password)
                if user:
                    st.session_state.usuario_autenticado = user
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

# SI EL USUARIO YA INGRESÓ: Configuración adaptativa de la mesa de trabajo
else:
    st.markdown("""
        <style>
        [data-testid="stHorizontalBlock"] { background-color: transparent !important; box-shadow: none !important; border-radius: 0 !important; padding: 0 !important; }
        
        /* --- FONDO GLOBAL ADAPTATIVO (GRISÁCEO OSCURO #212529 EN DARK MODE) --- */
        .stApp { 
            background-image: none !important; 
            background-color: light-dark(#f8fafc, #212529) !important; 
        }
        .stApp::before { display: none !important; }

        /* Fondo azul del menú lateral */
        .stApp [data-testid="stSidebar"] {
            background-color: #2563eb !important;
            background-image: linear-gradient(180deg, #1e3a8a 0%, #2563eb 100%) !important;
            color: #ffffff !important;
        }
        .stApp [data-testid="stSidebar"] div, 
        .stApp [data-testid="stSidebar"] span,
        .stApp [data-testid="stSidebar"] button,
        .stApp [data-testid="stSidebar"] p,
        .stApp [data-testid="stSidebar"] h2 {
            color: #ffffff !important;
        }

        /* Contenedores de formularios y tarjetas de visualización */
        .stApp [data-testid="stVerticalBlockBorderWrapper"], 
        .stApp [data-testid="stVerticalBlockBorderWrapper"] > div, 
        .stApp .header-card, 
        .stApp div[style*="background-color: #ffffff"],
        .stApp div[style*="background-color: rgb(255, 255, 255)"],
        .stApp div[style*="background-color:#ffffff"] {
            background-color: light-dark(#ffffff, #212529) !important; 
            background: light-dark(#ffffff, #212529) !important;
            border-color: light-dark(#e2e8f0, #475569) !important;
        }

        /* --- CONTROL DE LABELS (Negro en Light Mode, Blanco de alta legibilidad en Dark Mode) --- */
        .stApp label, 
        .stApp [data-testid="stWidgetLabel"] p,
        .stApp p[style*="font-weight: 800"], 
        .stApp p[style*="font-weight:700"] {
            color: light-dark(#000000, #ffffff) !important;
        }

        /* Títulos de secciones generales */
        .stApp h2, .stApp h3, .stApp h4, [id*="mis-rendiciones-recientes"] {
            color: light-dark(#1e3a8a, #ffffff) !important;
        }
        
        /* --- CORRECCIÓN DE CONTRASTE DEL BADGE "PENDIENTE" --- */
        .stApp [style*="background-color"] span,
        .stApp span[style*="background-color"] {
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            font-weight: 700 !important;
        }
        
        /* Párrafos e información secundaria dentro de las tarjetas */
        .stApp div p {
            color: light-dark(#334155, #cbd5e1) !important;
        }

        /* --- 🛠️ FIJAR TIPOGRAFÍA BLANCA EXCLUSIVA PARA EL SIDEBAR (Anula el error de image_c94d7c.png) --- */
        .sidebar-title-custom {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 800 !important;
        }
        .sidebar-text-custom {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        /* Inputs (Fondo Negro #121212 y Bordes/Letras Blancas en Dark Mode) */
        .stApp input, 
        .stApp select, 
        .stApp div[role="combobox"] button, 
        .stApp .stNumberInput div,
        .stApp div[data-baseweb="input"],
        .stApp div[data-baseweb="select"] {
            background-color: light-dark(#ffffff, #121212) !important; 
            color: light-dark(#0f172a, #ffffff) !important;
            border: 2px solid light-dark(#94a3b8, #ffffff) !important;
            border-radius: 6px !important;
        }
        
        .stApp input {
            color: light-dark(#0f172a, #ffffff) !important;
            -webkit-text-fill-color: light-dark(#0f172a, #ffffff) !important;
        }
        
        .stApp [data-testid="stFileUploader"] {
            background-color: light-dark(#ffffff, #121212) !important;
            border: 1px dashed light-dark(#cbd5e1, #ffffff) !important;
        }

        /* --- BOTONES DE ACCIÓN --- */
        .stApp div.stButton > button {
            background-color: light-dark(#1e3a8a, #ffffff) !important;
            border: 2px solid light-dark(#1e3a8a, #ffffff) !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease !important;
        }
        
        .stApp div.stButton > button,
        .stApp div.stButton > button * {
            color: light-dark(#ffffff, #212529) !important;
            -webkit-text-fill-color: light-dark(#ffffff, #212529) !important;
            font-weight: 700 !important;
        }
        
        .stApp div.stButton > button:hover {
            background-color: light-dark(#11254c, #121212) !important;
            border-color: light-dark(#11254c, #ffffff) !important;
        }
        .stApp div.stButton > button:hover * {
            color: light-dark(#ffffff, #ffffff) !important;
            -webkit-text-fill-color: light-dark(#ffffff, #ffffff) !important;
        }
        
        /* --- BOTÓN 'CERRAR SESIÓN' EN LA BARRA LATERAL --- */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: light-dark(#ffffff, #212529) !important; 
            border: 2px solid light-dark(#1e3a8a, #475569) !important; 
            border-radius: 12px !important;
            transition: all 0.2s ease-in-out !important;
        }
        [data-testid="stSidebar"] div.stButton > button * {
            color: light-dark(#1e3a8a, #ffffff) !important;
            -webkit-text-fill-color: light-dark(#1e3a8a, #ffffff) !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #ef4444 !important; 
            border-color: #ef4444 !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    user_logueado = st.session_state.usuario_autenticado
    
    st.sidebar.markdown(f"""
        <div style='padding: 10px 0px;'>
            <h2 class="sidebar-title-custom" style='margin:0; font-size:22px; font-weight:800;'>FinTrack Pro</h2>
            <p class="sidebar-text-custom" style='font-size:12px; margin:0;'>Usuario: {user_logueado['nombre']}</p>
            <span style='background-color: #2563eb; color: #ffffff; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 700;'>{user_logueado['rol']}</span>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_autenticado = None
        st.rerun()

    if user_logueado["rol"] == "Rendidor":
        rendidor.renderizar_vista(repositorio, caso_uso, user_logueado)
    elif user_logueado["rol"] == "Bandeja Auditoria":
        revision.renderizar_vista(repositorio, caso_uso)
    elif user_logueado["rol"] == "Gerencia Finanzas": 
        gerencia.renderizar_vista(repositorio, caso_uso)
    elif user_logueado["rol"] == "Cierre Tesoreria":
        tesoreria.renderizar_vista(repositorio, caso_uso)