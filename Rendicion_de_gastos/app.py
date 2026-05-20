import streamlit as st
from infraestructura.base_datos import RepositorioRendicionMemory
from aplicacion.flujos import CasoUsoRendicion
from interfaz import rendidor, revision, tesoreria

# Configuración inicial de la página
st.set_page_config(page_title="FinTrack Pro", layout="wide")

repositorio = RepositorioRendicionMemory()
caso_uso = CasoUsoRendicion(repositorio)

if "usuario_autenticado" not in st.session_state:
    st.session_state.usuario_autenticado = None

# SINO HAY USUARIO: Aplicamos el CSS exclusivo de la tarjeta de Login
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
        
        /* Contenedor de la Tarjeta del Login */
        [data-testid="stHorizontalBlock"] {
            background-color: #ffffff !important;
            border-radius: 28px !important;
            box-shadow: 0 30px 60px -12px rgba(15, 23, 42, 0.25) !important;
            max-width: 920px !important;  
            margin: 80px auto !important;
            overflow: hidden !important;
        }
        [data-testid="stHorizontalBlock"] > div:first-child {
            background: linear-gradient(135deg, #11254c 0%, #1e3a8a 100%) !important;
            padding: 50px !important; color: white !important;
            display: flex !important; flex-direction: column !important; justify-content: center !important;
        }
        [data-testid="stHorizontalBlock"] > div:last-child {
            background-color: #ffffff !important; padding: 50px !important; 
            display: flex !important; flex-direction: column !important; justify-content: center !important;
        }
        .stTextInput>div>div>input {
            border-radius: 30px !important; border: 2px solid #0f172a !important; padding: 12px 20px !important;        
            background-color: #ffffff !important; color: #0f172a !important;
        }
        .stButton>button {
            background-color: #0f172a !important; color: #ffffff !important; border-radius: 30px !important;
            padding: 12px 30px !important; font-weight: 700 !important; width: 100% !important; margin-top: 15px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.markdown('<p style="color:#ffffff; font-size:26px; font-weight:800; margin:0;">Welcome Back!</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#cbd5e1; font-size:14px; margin-top:12px; line-height:1.6;">Plataforma integrada para la carga técnica, validación automatizada y conciliación de gastos corporativos financieros.</p>', unsafe_allow_html=True)
        
    with col_der:
        st.markdown('<p style="color:#1e3a8a; font-size:20px; font-weight:800; margin:0; text-align:center;">FinTrack Pro</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#64748b; font-size:14px; text-align:center; margin-bottom:25px; margin-top:4px;">Ingresa tus credenciales para continuar</p>', unsafe_allow_html=True)
        
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

# SI EL USUARIO YA INGRESÓ: Limpiamos la pantalla y cargamos los roles
else:
    user_logueado = st.session_state.usuario_autenticado
    
    st.sidebar.markdown(f"""
        <div style='padding: 10px 0px;'>
            <h2 style='color: #0f172a; margin:0; font-size:22px; font-weight:800;'>FinTrack Pro</h2>
            <p style='color: #64748b; font-size:12px; margin:0;'>Usuario: {user_logueado['nombre']}</p>
            <span style='background-color: #1e3a8a; color: #ffffff; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 700;'>{user_logueado['rol']}</span>
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
    elif user_logueado["rol"] == "Cierre Tesoreria":
        tesoreria.renderizar_vista(repositorio, caso_uso)