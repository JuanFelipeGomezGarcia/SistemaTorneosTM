import streamlit as st
from database.db_operations import DatabaseOperations
from pages.vista_cuadros import vista_cuadros_page
from pages.vista_llaves import vista_llaves_page
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Torneos - Tenis de Mesa",
    page_icon="🏓",
    layout="wide"
)

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
    """Página de login"""
    st.title("🏓 Sistema de Torneos - Tenis de Mesa")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Selecciona tu tipo de usuario")
        
        user_type = st.radio(
            "Tipo de usuario:",
            ["Administrador", "Competidor"],
            horizontal=True
        )
        
        if user_type == "Administrador":
            st.subheader("Iniciar Sesión - Administrador")
            
            with st.form("admin_login"):
                usuario = st.text_input("Usuario")
                password = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("Iniciar Sesión")
                
                if submit:
                    if db.verificar_admin(usuario, password):
                        st.session_state.user_type = "admin"
                        st.session_state.authenticated = True
                        st.session_state.current_page = 'home'
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
        
        else:  # Competidor
            if st.button("Continuar como Competidor"):
                st.session_state.user_type = "competitor"
                st.session_state.authenticated = True
                st.session_state.current_page = 'home'
                st.rerun()

def home_page():
    """Página principal con lista de torneos"""
    st.title("🏓 Torneos de Tenis de Mesa")
    
    # Botón de logout
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Cerrar Sesión"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
    # Mostrar tipo de usuario
    user_icon = "👨‍💼" if st.session_state.user_type == "admin" else "🏓"
    user_text = "Administrador" if st.session_state.user_type == "admin" else "Competidor"
    st.markdown(f"{user_icon} **Usuario:** {user_text}")
    
    st.markdown("---")
    
    # Botón crear torneo (solo admin)
    if st.session_state.user_type == "admin":
        if st.button("➕ Crear Nuevo Torneo"):
            st.session_state.current_page = 'crear_torneo'
            st.rerun()
        st.markdown("---")
    
    # Lista de torneos
    st.subheader("Torneos Disponibles")
    
    torneos = db.obtener_torneos()
    
    if not torneos:
        st.info("No hay torneos disponibles")
        return
    
    for torneo in torneos:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"**{torneo['nombre']}**")
            
            with col2:
                st.write(f"📅 {torneo['fecha']}")
            
            with col3:
                estado_color = "🟢" if torneo['estado'] == 'en_curso' else "🔴"
                estado_text = "En Curso" if torneo['estado'] == 'en_curso' else "Finalizado"
                st.write(f"{estado_color} {estado_text}")
            
            with col4:
                if st.button("Ver", key=f"ver_torneo_{torneo['id']}"):
                    st.session_state.selected_tournament = torneo
                    st.session_state.current_page = 'vista_categorias'
                    st.rerun()
        
        st.markdown("---")

def crear_torneo_page():
    """Página para crear un nuevo torneo"""
    st.title("➕ Crear Nuevo Torneo")
    
    if st.button("← Volver al Home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("---")
    
    # Formulario de creación de torneo
    with st.form("crear_torneo_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_torneo = st.text_input("Nombre del Torneo")
        
        with col2:
            fecha_torneo = st.date_input("Fecha del Torneo", value=datetime.now())
        
        submit = st.form_submit_button("Crear Torneo")
        
        if submit and nombre_torneo:
            torneo_id = db.crear_torneo(nombre_torneo, fecha_torneo)
            if torneo_id:
                st.success("Torneo creado exitosamente!")
                # Cargar el torneo recién creado
                torneos = db.obtener_torneos()
                for torneo in torneos:
                    if torneo['id'] == torneo_id:
                        st.session_state.selected_tournament = torneo
                        break
                st.session_state.current_page = 'editar_torneo'
                st.rerun()
            else:
                st.error("Error al crear el torneo")

def editar_torneo_page():
    """Página para editar torneo (agregar categorías)"""
    torneo = st.session_state.selected_tournament
    
    st.title(f"📝 Editando: {torneo['nombre']}")
    st.write(f"📅 Fecha: {torneo['fecha']}")
    
    if st.button("← Volver al Home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener categorías existentes
    categorias = db.obtener_categorias(torneo['id'])
    
    # Botón para agregar nueva categoría
    if st.button("➕ Agregar Nueva Categoría"):
        st.session_state.current_page = 'crear_categoria'
        st.rerun()
    
    st.markdown("---")
    
    # Mostrar categorías existentes
    if categorias:
        st.subheader("Categorías del Torneo")
        
        for categoria in categorias:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{categoria['nombre']}**")
                
                with col2:
                    st.write(f"Cuadros: {categoria['cantidad_cuadros']}")
                
                with col3:
                    st.write(f"Personas/Cuadro: {categoria['personas_por_cuadro']}")
                
                with col4:
                    if st.button("Editar", key=f"edit_cat_{categoria['id']}"):
                        st.session_state.selected_category = categoria
                        st.session_state.current_page = 'crear_categoria'
                        st.rerun()
            
            st.markdown("---")
        
        # Botón para finalizar creación del torneo
        if st.button("✅ Finalizar Creación del Torneo"):
            st.session_state.current_page = 'home'
            st.success("Torneo creado exitosamente!")
            st.rerun()
    else:
        st.info("No hay categorías creadas. Agrega al menos una categoría para continuar.")

def crear_categoria_page():
    """Página para crear/editar una categoría"""
    torneo = st.session_state.selected_tournament
    categoria = st.session_state.get('selected_category', None)
    
    titulo = "✏️ Editar Categoría" if categoria else "➕ Crear Nueva Categoría"
    st.title(titulo)
    st.write(f"Torneo: {torneo['nombre']}")
    
    if st.button("← Volver"):
        st.session_state.selected_category = None
        st.session_state.current_page = 'editar_torneo'
        st.rerun()
    
    st.markdown("---")
    
    # Formulario de categoría
    with st.form("categoria_form"):
        # Valores por defecto si estamos editando
        nombre_default = categoria['nombre'] if categoria else ""
        cuadros_default = categoria['cantidad_cuadros'] if categoria else 1
        personas_default = categoria['personas_por_cuadro'] if categoria else 4
        
        nombre_categoria = st.text_input("Nombre de la Categoría", value=nombre_default)
        
        col1, col2 = st.columns(2)
        with col1:
            cantidad_cuadros = st.number_input("Cantidad de Cuadros", min_value=1, max_value=10, value=cuadros_default)
        
        with col2:
            personas_por_cuadro = st.number_input("Personas por Cuadro", min_value=2, max_value=8, value=personas_default)
        
        # Lista de participantes
        st.subheader("Participantes")
        
        # Obtener participantes existentes si estamos editando
        participantes_existentes = []
        if categoria:
            participantes_data = db.obtener_participantes(categoria['id'])
            participantes_existentes = [p['nombre'] for p in participantes_data]
        
        # Campo para agregar participantes
        participantes_text = st.text_area(
            "Lista de Participantes (uno por línea)",
            value="\n".join(participantes_existentes),
            height=200
        )
        
        submit = st.form_submit_button("Guardar Categoría")
        
        if submit and nombre_categoria:
            participantes_lista = [p.strip() for p in participantes_text.split('\n') if p.strip()]
            
            if categoria:
                # Actualizar categoría existente
                if db.actualizar_categoria(categoria['id'], nombre_categoria, cantidad_cuadros, personas_por_cuadro):
                    # Actualizar participantes (simplificado - eliminar y recrear)
                    # En una implementación completa, sería mejor hacer un merge
                    st.success("Categoría actualizada exitosamente!")
                else:
                    st.error("Error al actualizar la categoría")
            else:
                # Crear nueva categoría
                categoria_id = db.crear_categoria(torneo['id'], nombre_categoria, cantidad_cuadros, personas_por_cuadro)
                if categoria_id:
                    # Agregar participantes
                    for participante in participantes_lista:
                        db.agregar_participante(categoria_id, participante)
                    st.success("Categoría creada exitosamente!")
                else:
                    st.error("Error al crear la categoría")
            
            # Volver a la página anterior
            st.session_state.selected_category = None
            st.session_state.current_page = 'editar_torneo'
            st.rerun()

def vista_categorias_page():
    """Página que muestra las categorías de un torneo"""
    torneo = st.session_state.selected_tournament
    
    st.title(f"🏓 {torneo['nombre']}")
    st.write(f"📅 Fecha: {torneo['fecha']}")
    
    # Botón volver
    if st.button("← Volver al Home"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener categorías
    categorias = db.obtener_categorias(torneo['id'])
    
    if not categorias:
        st.info("Este torneo no tiene categorías configuradas")
        return
    
    st.subheader("Categorías del Torneo")
    
    for categoria in categorias:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"**{categoria['nombre']}**")
            
            with col2:
                st.write(f"Cuadros: {categoria['cantidad_cuadros']}")
            
            with col3:
                participantes = db.obtener_participantes(categoria['id'])
                st.write(f"Participantes: {len(participantes)}")
            
            with col4:
                if st.button("Ver", key=f"ver_cat_{categoria['id']}"):
                    st.session_state.selected_category = categoria
                    st.session_state.current_page = 'vista_cuadros'
                    st.rerun()
        
        st.markdown("---")
    
    # Botón terminar torneo (solo admin y si todas las categorías tienen ganador)
    if st.session_state.user_type == "admin" and torneo['estado'] == 'en_curso':
        todas_completas = all(cat.get('ganador') for cat in categorias)
        
        if todas_completas:
            if st.button("🏆 Terminar Torneo"):
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