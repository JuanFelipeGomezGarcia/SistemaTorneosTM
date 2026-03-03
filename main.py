import streamlit as st
# Limpiar comentarios innecesarios
from database.db_operations import DatabaseOperations
from pages.vista_cuadros import vista_cuadros_page
from pages.vista_llaves import vista_llaves_page
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Torneos - Tenis de Mesa",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar sidebar + CSS Premium Global
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .css-1d391kg {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* ── Hero Headers ── */
    .premium-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 32px 36px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
    }
    .premium-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .premium-hero h1 {
        color: white;
        margin: 0;
        font-size: 30px;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .premium-hero p {
        color: rgba(255,255,255,0.85);
        margin: 8px 0 0 0;
        font-size: 15px;
    }
    .premium-hero .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.18);
        backdrop-filter: blur(8px);
        padding: 6px 14px;
        border-radius: 20px;
        color: white;
        font-size: 13px;
        font-weight: 600;
        margin-top: 12px;
    }
    
    /* ── Cards ── */
    .premium-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    .premium-card:hover {
        box-shadow: 0 6px 24px rgba(0,0,0,0.08);
        transform: translateY(-2px);
        border-color: #cbd5e1;
    }
    .premium-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .premium-card-title {
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .premium-card-subtitle {
        font-size: 13px;
        color: #64748b;
        margin: 4px 0 0 0;
    }
    
    /* ── Status Badges ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    .status-active {
        background: #dcfce7;
        color: #166534;
    }
    .status-finished {
        background: #fee2e2;
        color: #991b1b;
    }
    .status-admin {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    .status-competitor {
        background: #dbeafe;
        color: #1d4ed8;
    }
    
    /* ── Metric Cards ── */
    .metric-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.05));
        border: 1px solid rgba(102,126,234,0.15);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        font-family: 'Inter', sans-serif;
    }
    .metric-card .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #667eea;
        margin: 0;
    }
    .metric-card .metric-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        margin: 4px 0 0 0;
    }
    
    /* ── Login Card ── */
    .login-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 36px 40px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        font-family: 'Inter', sans-serif;
    }
    .login-card h3 {
        color: #1e293b;
        font-size: 18px;
        font-weight: 700;
        margin: 0 0 20px 0;
    }
    
    /* ── Section Headers ── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #1e293b;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ── Form styling ── */
    .form-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 28px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
    }
    
    /* ── Empty State ── */
    .empty-state {
        text-align: center;
        padding: 48px 24px;
        font-family: 'Inter', sans-serif;
    }
    .empty-state .empty-icon {
        font-size: 48px;
        margin-bottom: 12px;
    }
    .empty-state .empty-text {
        font-size: 16px;
        color: #64748b;
        font-weight: 500;
    }
    
    /* ── Category Cards ── */
    .cat-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 12px;
        border-left: 4px solid #667eea;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    .cat-card:hover {
        box-shadow: 0 4px 16px rgba(102,126,234,0.12);
        transform: translateX(4px);
    }
    .cat-card-name {
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
    }
    .cat-card-info {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        background: #f1f5f9;
        padding: 3px 10px;
        border-radius: 8px;
    }
    
    /* ── Date badge ── */
    .date-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar base de datos
db = DatabaseOperations()

# Inicializar session state
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'
if 'selected_tournament' not in st.session_state:
    st.session_state.selected_tournament = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None

def login_page():
    """Página de login — Premium"""
    st.markdown("""
    <div class='premium-hero' style='text-align:center; padding:48px 36px;'>
        <h1>🏓 Sistema de Torneos</h1>
        <p>Tenis de Mesa — Gestión profesional de torneos</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h3>👤 Selecciona tu tipo de usuario</h3>", unsafe_allow_html=True)
        
        user_type = st.radio(
            "Tipo de usuario:",
            ["Administrador", "Competidor"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if user_type == "Administrador":
            st.markdown("---")
            st.markdown("<h3>🔐 Iniciar Sesión — Administrador</h3>", unsafe_allow_html=True)
            
            with st.form("admin_login"):
                usuario = st.text_input("👤 Usuario")
                password = st.text_input("🔑 Contraseña", type="password")
                st.markdown("")
                submit = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)
                
                if submit:
                    if not usuario or not password:
                        st.error("Por favor completa todos los campos")
                    elif db.verificar_admin(usuario, password):
                        st.session_state.user_type = "admin"
                        st.session_state.authenticated = True
                        st.session_state.current_page = 'home'
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
        
        else:  # Competidor
            st.markdown("---")
            st.markdown("""
            <div style='text-align:center; padding:20px 0;'>
                <p style='color:#64748b; font-family:Inter,sans-serif; font-size:14px;'>
                    Accede como espectador para ver los torneos, cuadros y llaves en tiempo real
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🏓 Continuar como Competidor", type="primary", use_container_width=True):
                st.session_state.user_type = "competitor"
                st.session_state.authenticated = True
                st.session_state.current_page = 'home'
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def home_page():
    """Página principal con lista de torneos — Premium"""
    # Hero header
    user_icon = "👨‍💼" if st.session_state.user_type == "admin" else "🏓"
    user_text = "Administrador" if st.session_state.user_type == "admin" else "Competidor"
    badge_class = "status-admin" if st.session_state.user_type == "admin" else "status-competitor"
    
    st.markdown(f"""
    <div class='premium-hero'>
        <h1>🏓 Torneos de Tenis de Mesa</h1>
        <p>Panel de gestión y seguimiento de torneos</p>
        <span class='hero-badge'>{user_icon} {user_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout
    col_spacer, col_logout = st.columns([5, 1])
    with col_logout:
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Crear torneo (admin only)
    if st.session_state.user_type == "admin":
        if st.button("➕ Crear Nuevo Torneo", type="primary"):
            st.session_state.selected_tournament = None
            st.session_state.selected_category = None
            st.session_state.current_page = 'crear_torneo'
            st.rerun()
    
    # Lista de torneos
    st.markdown("<div class='section-header'>📋 Torneos Disponibles</div>", unsafe_allow_html=True)
    
    torneos = db.obtener_torneos()
    
    if not torneos:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-icon'>📭</div>
            <div class='empty-text'>No hay torneos disponibles</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for torneo in torneos:
        # Card HTML header
        estado_class = "status-active" if torneo['estado'] == 'en_curso' else "status-finished"
        estado_text = "🟢 En Curso" if torneo['estado'] == 'en_curso' else "🔴 Finalizado"
        
        st.markdown(f"""
        <div class='premium-card'>
            <div class='premium-card-header'>
                <div>
                    <p class='premium-card-title'>{torneo['nombre']}</p>
                    <p class='premium-card-subtitle'>📅 {torneo['fecha']}</p>
                </div>
                <span class='status-badge {estado_class}'>{estado_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Buttons row
        if st.session_state.user_type == "admin":
            btn_col1, btn_col2, btn_spacer = st.columns([1, 1, 4])
        else:
            btn_col1, btn_spacer = st.columns([1, 5])
        
        with btn_col1:
            if st.button("👁️ Ver Torneo", key=f"ver_torneo_{torneo['id']}", use_container_width=True):
                st.session_state.selected_tournament = torneo
                st.session_state.current_page = 'vista_categorias'
                st.rerun()
        
        if st.session_state.user_type == "admin":
            with btn_col2:
                if st.button("🗑️ Eliminar", key=f"del_torneo_{torneo['id']}", type="secondary", use_container_width=True):
                    st.session_state[f'confirm_delete_torneo_{torneo["id"]}'] = True
        
        # Delete confirmation
        if st.session_state.get(f'confirm_delete_torneo_{torneo["id"]}'):
            st.warning(f"⚠️ ¿Estás seguro de eliminar **{torneo['nombre']}**? Se borrarán todas sus categorías, participantes, partidos y llaves. Esta acción no se puede deshacer.")
            c_yes, c_no, c_space = st.columns([1, 1, 4])
            with c_yes:
                if st.button("✅ Sí, eliminar", key=f"yes_del_torneo_{torneo['id']}", type="primary", use_container_width=True):
                    if db.eliminar_torneo(torneo['id']):
                        st.session_state.pop(f'confirm_delete_torneo_{torneo["id"]}', None)
                        st.success(f"✅ Torneo '{torneo['nombre']}' eliminado")
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar el torneo")
            with c_no:
                if st.button("❌ Cancelar", key=f"no_del_torneo_{torneo['id']}", use_container_width=True):
                    st.session_state.pop(f'confirm_delete_torneo_{torneo["id"]}', None)
                    st.rerun()
        
        st.markdown("")

def crear_torneo_page():
    """Página para crear un nuevo torneo — Premium"""
    st.markdown("""
    <div class='premium-hero'>
        <h1>➕ Crear Nuevo Torneo</h1>
        <p>Configura un nuevo torneo de tenis de mesa</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver al Home", type="secondary"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("<div class='section-header'>📝 Datos del Torneo</div>", unsafe_allow_html=True)
    
    with st.form("crear_torneo_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_torneo = st.text_input("🏆 Nombre del Torneo")
        
        with col2:
            fecha_torneo = st.date_input("📅 Fecha del Torneo", value=datetime.now())
        
        st.markdown("")
        submit = st.form_submit_button("🏆 Crear Torneo", type="primary", use_container_width=True)
        
        if submit:
            if not nombre_torneo or not nombre_torneo.strip():
                st.error("❌ El nombre del torneo es obligatorio")
            else:
                torneo_id = db.crear_torneo(nombre_torneo.strip(), fecha_torneo)
                if torneo_id:
                    st.success("✅ Torneo creado exitosamente!")
                    torneos = db.obtener_torneos()
                    for torneo in torneos:
                        if torneo['id'] == torneo_id:
                            st.session_state.selected_tournament = torneo
                            break
                    st.session_state.current_page = 'editar_torneo'
                    st.rerun()
                else:
                    st.error("❌ Error al crear el torneo")

def editar_torneo_page():
    """Página para editar torneo (agregar categorías) — Premium"""
    torneo = st.session_state.selected_tournament
    
    st.markdown(f"""
    <div class='premium-hero'>
        <h1>📝 {torneo['nombre']}</h1>
        <p>📅 {torneo['fecha']} &nbsp;•&nbsp; Configuración del torneo</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("← Volver al Home", type="secondary", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
    
    # Obtener categorías existentes
    categorias = db.obtener_categorias(torneo['id'])
    
    # Botón para agregar nueva categoría
    st.markdown("<div class='section-header'>📂 Categorías del Torneo</div>", unsafe_allow_html=True)
    
    if st.button("➕ Agregar Nueva Categoría", type="primary"):
        st.session_state.selected_category = None
        if 'participantes_input' in st.session_state:
            del st.session_state['participantes_input']
        if 'personas_cuadro' in st.session_state:
            del st.session_state['personas_cuadro']
        if 'personas_pasan' in st.session_state:
            del st.session_state['personas_pasan']
        st.session_state.current_page = 'crear_categoria'
        st.rerun()
    
    st.markdown("")
    
    # Mostrar categorías existentes
    if categorias:
        for categoria in categorias:
            # Card HTML
            st.markdown(f"""
            <div class='cat-card'>
                <div class='premium-card-header'>
                    <div>
                        <span class='cat-card-name'>{categoria['nombre']}</span>
                    </div>
                    <div>
                        <span class='cat-card-info'>🟦 {categoria['cantidad_cuadros']} cuadros</span>
                        &nbsp;
                        <span class='cat-card-info'>👥 {categoria['personas_por_cuadro']} por cuadro</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            btn_c1, btn_c2, btn_spacer = st.columns([1, 1, 4])
            with btn_c1:
                if st.button("✏️ Editar", key=f"edit_cat_{categoria['id']}", use_container_width=True):
                    st.session_state.selected_category = categoria
                    st.session_state.current_page = 'crear_categoria'
                    st.rerun()
            with btn_c2:
                if st.button("🗑️ Eliminar", key=f"del_cat_{categoria['id']}", type="secondary", use_container_width=True):
                    st.session_state[f'confirm_delete_{categoria["id"]}'] = True
            
            # Delete confirmation
            if st.session_state.get(f'confirm_delete_{categoria["id"]}'):
                st.warning(f"¿Estás seguro de eliminar **{categoria['nombre']}**? Se borrarán todos sus participantes, partidos y llaves.")
                c_yes, c_no, c_s = st.columns([1, 1, 4])
                with c_yes:
                    if st.button("✅ Sí, eliminar", key=f"yes_del_{categoria['id']}", type="primary", use_container_width=True):
                        if db.eliminar_categoria(categoria['id']):
                            st.session_state.pop(f'confirm_delete_{categoria["id"]}', None)
                            st.success(f"✅ Categoría '{categoria['nombre']}' eliminada")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar la categoría")
                with c_no:
                    if st.button("❌ Cancelar", key=f"no_del_{categoria['id']}", use_container_width=True):
                        st.session_state.pop(f'confirm_delete_{categoria["id"]}', None)
                        st.rerun()
            
            st.markdown("")
        
        # Finalizar
        st.markdown("---")
        col_fin1, col_fin2, col_fin3 = st.columns([1, 2, 1])
        with col_fin2:
            if st.button("✅ Finalizar Creación del Torneo", type="primary", use_container_width=True):
                st.session_state.current_page = 'home'
                st.success("✅ Torneo creado exitosamente!")
                st.rerun()
    else:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-icon'>📂</div>
            <div class='empty-text'>No hay categorías creadas. Agrega al menos una categoría para continuar.</div>
        </div>
        """, unsafe_allow_html=True)

def crear_categoria_page():
    """Página para crear/editar una categoría — Premium"""
    torneo = st.session_state.selected_tournament
    categoria = st.session_state.get('selected_category', None)
    
    titulo = "✏️ Editar Categoría" if categoria else "➕ Nueva Categoría"
    subtitulo = f"Categoría: {categoria['nombre']}" if categoria else "Configura una nueva categoría para el torneo"
    
    st.markdown(f"""
    <div class='premium-hero'>
        <h1>{titulo}</h1>
        <p>🏆 {torneo['nombre']} &nbsp;•&nbsp; {subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("← Volver", type="secondary", use_container_width=True):
            st.session_state.selected_category = None
            if 'participantes_input' in st.session_state:
                del st.session_state['participantes_input']
            if 'personas_cuadro' in st.session_state:
                del st.session_state['personas_cuadro']
            if 'personas_pasan' in st.session_state:
                del st.session_state['personas_pasan']
            st.session_state.current_page = 'editar_torneo'
            st.rerun()
    
    # Obtener participantes existentes si estamos editando
    participantes_existentes = []
    if categoria:
        participantes_data = db.obtener_participantes(categoria['id'])
        participantes_existentes = [p['nombre'] for p in participantes_data]
    
    # Participantes
    st.markdown("<div class='section-header'>👥 Participantes</div>", unsafe_allow_html=True)
    
    participantes_text = st.text_area(
        "Lista de Participantes (uno por línea)",
        value="\n".join(participantes_existentes),
        height=200,
        help="Escribe el nombre de cada participante en una línea separada",
        key="participantes_input",
        label_visibility="collapsed",
        placeholder="Escribe un participante por línea...\nEjemplo:\nJuan Pérez\nMaría García\nCarlos López"
    )
    
    # Contador
    participantes_actuales = [p.strip() for p in participantes_text.split('\n') if p.strip()]
    total_participantes = len(participantes_actuales)
    
    # Configuración
    st.markdown("<div class='section-header'>⚙️ Configuración de Cuadros</div>", unsafe_allow_html=True)
    
    personas_default = categoria['personas_por_cuadro'] if categoria else 4
    personas_pasan_default = categoria.get('personas_que_pasan', 2) if categoria else 2
    
    col1, col2 = st.columns(2)
    with col1:
        personas_por_cuadro = st.number_input(
            "👥 Personas por Cuadro", 
            min_value=2, 
            max_value=8, 
            value=personas_default,
            help="Número de participantes en cada cuadro Round Robin",
            key="personas_cuadro"
        )
    
    with col2:
        personas_que_pasan = st.number_input(
            "🏆 Personas que pasan a Llaves", 
            min_value=1, 
            max_value=personas_por_cuadro, 
            value=min(personas_pasan_default, personas_por_cuadro),
            help="Cuántos participantes de cada cuadro avanzan a la fase eliminatoria",
            key="personas_pasan"
        )
    
    # Métricas en tiempo real
    if total_participantes > 0:
        cuadros_necesarios = (total_participantes + personas_por_cuadro - 1) // personas_por_cuadro
        participantes_en_llaves = cuadros_necesarios * personas_que_pasan
        
        st.markdown("<div class='section-header'>📊 Resumen</div>", unsafe_allow_html=True)
        
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-value'>{total_participantes}</p>
                <p class='metric-label'>👥 Participantes</p>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-value'>{cuadros_necesarios}</p>
                <p class='metric-label'>🟦 Cuadros</p>
            </div>
            """, unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""
            <div class='metric-card'>
                <p class='metric-value'>{participantes_en_llaves}</p>
                <p class='metric-label'>🏆 Pasan a Llaves</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # Validaciones
        if total_participantes < personas_por_cuadro:
            st.warning(f"⚠️ Necesitas al menos {personas_por_cuadro} participantes para formar un cuadro")
        elif personas_que_pasan > personas_por_cuadro:
            st.error(f"❌ Las personas que pasan ({personas_que_pasan}) no pueden ser mayores que las personas por cuadro ({personas_por_cuadro})")
        else:
            st.success(f"✅ Configuración válida: {cuadros_necesarios} cuadro(s) con {personas_por_cuadro} personas cada uno")
    
    # Formulario de guardado
    st.markdown("<div class='section-header'>💾 Guardar</div>", unsafe_allow_html=True)
    
    with st.form("categoria_form"):
        nombre_default = categoria['nombre'] if categoria else ""
        nombre_categoria = st.text_input("🏷️ Nombre de la Categoría", value=nombre_default)
        
        st.markdown("")
        submit = st.form_submit_button("💾 Guardar Categoría", type="primary", use_container_width=True)
        
        if submit and nombre_categoria:
            participantes_text_final = st.session_state.get('participantes_input', '')
            participantes_lista = [p.strip() for p in participantes_text_final.split('\n') if p.strip()]
            personas_por_cuadro_final = st.session_state.get('personas_cuadro', 4)
            personas_que_pasan_final = st.session_state.get('personas_pasan', 2)
            
            if not nombre_categoria.strip():
                st.error("❌ El nombre de la categoría es obligatorio")
                return
            
            if len(participantes_lista) < personas_por_cuadro_final:
                st.error(f"❌ Necesitas al menos {personas_por_cuadro_final} participantes")
                return
            
            if personas_que_pasan_final > personas_por_cuadro_final:
                st.error(f"❌ Las personas que pasan no pueden ser mayor a las personas por cuadro")
                return
            
            cantidad_cuadros = (len(participantes_lista) + personas_por_cuadro_final - 1) // personas_por_cuadro_final
            
            if categoria:
                if db.actualizar_categoria(categoria['id'], nombre_categoria.strip(), cantidad_cuadros, personas_por_cuadro_final):
                    st.success("✅ Categoría actualizada exitosamente!")
                else:
                    st.error("❌ Error al actualizar la categoría")
            else:
                categoria_id = db.crear_categoria(torneo['id'], nombre_categoria.strip(), cantidad_cuadros, personas_por_cuadro_final)
                if categoria_id:
                    for participante in participantes_lista:
                        db.agregar_participante(categoria_id, participante)
                    st.success("✅ Categoría creada exitosamente!")
                else:
                    st.error("❌ Error al crear la categoría")
            
            st.session_state.selected_category = None
            if 'participantes_input' in st.session_state:
                del st.session_state['participantes_input']
            if 'personas_cuadro' in st.session_state:
                del st.session_state['personas_cuadro']
            if 'personas_pasan' in st.session_state:
                del st.session_state['personas_pasan']
            st.session_state.current_page = 'editar_torneo'
            st.rerun()

def vista_categorias_page():
    """Página que muestra las categorías de un torneo — Premium"""
    torneo = st.session_state.selected_tournament
    
    estado_badge = "🟢 En Curso" if torneo['estado'] == 'en_curso' else "🔴 Finalizado"
    
    st.markdown(f"""
    <div class='premium-hero'>
        <h1>🏓 {torneo['nombre']}</h1>
        <p>📅 {torneo['fecha']}</p>
        <span class='hero-badge'>{estado_badge}</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("← Volver al Home", type="secondary", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
    
    # Obtener categorías
    categorias = db.obtener_categorias(torneo['id'])
    
    if not categorias:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-icon'>📂</div>
            <div class='empty-text'>Este torneo no tiene categorías configuradas</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("<div class='section-header'>🏆 Categorías del Torneo</div>", unsafe_allow_html=True)
    
    for categoria in categorias:
        participantes = db.obtener_participantes(categoria['id'])
        num_participantes = len(participantes)
        
        st.markdown(f"""
        <div class='cat-card'>
            <div class='premium-card-header'>
                <div>
                    <span class='cat-card-name'>{categoria['nombre']}</span>
                </div>
                <div>
                    <span class='cat-card-info'>🟦 {categoria['cantidad_cuadros']} cuadros</span>
                    &nbsp;
                    <span class='cat-card-info'>👥 {num_participantes} participantes</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        btn_c1, btn_spacer = st.columns([1, 5])
        with btn_c1:
            if st.button("🎯 Ver Categoría", key=f"ver_cat_{categoria['id']}", use_container_width=True, type="primary"):
                st.session_state.selected_category = categoria
                st.session_state.current_page = 'vista_cuadros'
                st.rerun()
        
        st.markdown("")
    
    # Botón terminar torneo (solo admin y si todas las categorías tienen ganador)
    if st.session_state.user_type == "admin" and torneo['estado'] == 'en_curso':
        todas_completas = all(cat.get('ganador') for cat in categorias)
        
        if todas_completas:
            st.markdown("---")
            col_fin1, col_fin2, col_fin3 = st.columns([1, 2, 1])
            with col_fin2:
                if st.button("🏆 Terminar Torneo", type="primary", use_container_width=True):
                    if db.actualizar_estado_torneo(torneo['id'], 'finalizado'):
                        st.success("¡Torneo finalizado exitosamente!")
                        st.session_state.selected_tournament['estado'] = 'finalizado'
                        st.rerun()

# Función principal de navegación
def main():
    """Función principal que maneja la navegación"""
    
    # Verificar autenticación
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Navegación basada en la página actual
    if st.session_state.current_page == 'home':
        home_page()
    elif st.session_state.current_page == 'crear_torneo':
        crear_torneo_page()
    elif st.session_state.current_page == 'editar_torneo':
        editar_torneo_page()
    elif st.session_state.current_page == 'crear_categoria':
        crear_categoria_page()
    elif st.session_state.current_page == 'vista_categorias':
        vista_categorias_page()
    elif st.session_state.current_page == 'vista_cuadros':
        vista_cuadros_page()
    elif st.session_state.current_page == 'vista_llaves':
        vista_llaves_page()

if __name__ == "__main__":
    main()