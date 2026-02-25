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

# Ocultar sidebar completamente
st.markdown("""
<style>
    .css-1d391kg {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
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
            if st.button("Continuar como Competidor"):
                st.session_state.user_type = "competitor"
                st.session_state.authenticated = True
                st.session_state.current_page = 'home'
                st.rerun()

def home_page():
    """Página principal con lista de torneos"""
    st.title("🏓 Torneos de Tenis de Mesa")
    
    # Usuario y botón de logout en la esquina superior derecha
    col1, col2 = st.columns([6, 1])
    with col2:
        user_icon = "👨‍💼" if st.session_state.user_type == "admin" else "🏓"
        user_text = "Administrador" if st.session_state.user_type == "admin" else "Competidor"
        st.markdown(f"**{user_icon} {user_text}**")
        if st.button("Cerrar Sesión", type="secondary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Botón crear torneo (solo admin)
    if st.session_state.user_type == "admin":
        if st.button("➕ Crear Nuevo Torneo"):
            # Limpiar cualquier dato previo
            st.session_state.selected_tournament = None
            st.session_state.selected_category = None
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
            if st.session_state.user_type == "admin":
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            else:
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
            
            # Botón eliminar solo para admin
            if st.session_state.user_type == "admin":
                with col5:
                    if st.button("🗑️", key=f"del_torneo_{torneo['id']}", type="secondary", help=f"Eliminar {torneo['nombre']}"):
                        st.session_state[f'confirm_delete_torneo_{torneo["id"]}'] = True
            
            # Diálogo de confirmación para eliminar torneo
            if st.session_state.get(f'confirm_delete_torneo_{torneo["id"]}'):
                st.warning(f"⚠️ ¿Estás seguro de eliminar el torneo **{torneo['nombre']}**? Se borrarán todas sus categorías, participantes, partidos y llaves. Esta acción no se puede deshacer.")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("✅ Sí, eliminar torneo", key=f"yes_del_torneo_{torneo['id']}", type="primary"):
                        if db.eliminar_torneo(torneo['id']):
                            st.session_state.pop(f'confirm_delete_torneo_{torneo["id"]}', None)
                            st.success(f"✅ Torneo '{torneo['nombre']}' eliminado exitosamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el torneo")
                with c_no:
                    if st.button("❌ No, cancelar", key=f"no_del_torneo_{torneo['id']}"):
                        st.session_state.pop(f'confirm_delete_torneo_{torneo["id"]}', None)
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
        
        if submit:
            if not nombre_torneo or not nombre_torneo.strip():
                st.error("❌ El nombre del torneo es obligatorio")
            else:
                torneo_id = db.crear_torneo(nombre_torneo.strip(), fecha_torneo)
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
                    st.error("❌ Error al crear el torneo")

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
        # Limpiar selected_category para asegurar que se crea una nueva
        st.session_state.selected_category = None
        # Limpiar los campos del formulario
        if 'participantes_input' in st.session_state:
            del st.session_state['participantes_input']
        if 'personas_cuadro' in st.session_state:
            del st.session_state['personas_cuadro']
        if 'personas_pasan' in st.session_state:
            del st.session_state['personas_pasan']
        st.session_state.current_page = 'crear_categoria'
        st.rerun()
    
    st.markdown("---")
    
    # Mostrar categorías existentes
    if categorias:
        st.subheader("Categorías del Torneo")
        
        for categoria in categorias:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
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
                
                with col5:
                    if st.button("🗑️", key=f"del_cat_{categoria['id']}", type="secondary", help=f"Eliminar {categoria['nombre']}"):
                        st.session_state[f'confirm_delete_{categoria["id"]}'] = True
                
                # Diálogo de confirmación
                if st.session_state.get(f'confirm_delete_{categoria["id"]}'):
                    st.warning(f"¿Estás seguro de eliminar **{categoria['nombre']}**? Se borrarán todos sus participantes, partidos y llaves.")
                    c_yes, c_no = st.columns(2)
                    with c_yes:
                        if st.button("✅ Sí, eliminar", key=f"yes_del_{categoria['id']}", type="primary"):
                            if db.eliminar_categoria(categoria['id']):
                                st.session_state.pop(f'confirm_delete_{categoria["id"]}', None)
                                st.success(f"✅ Categoría '{categoria['nombre']}' eliminada")
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar la categoría")
                    with c_no:
                        if st.button("❌ No, cancelar", key=f"no_del_{categoria['id']}"):
                            st.session_state.pop(f'confirm_delete_{categoria["id"]}', None)
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
        # Limpiar los campos del formulario al volver
        if 'participantes_input' in st.session_state:
            del st.session_state['participantes_input']
        if 'personas_cuadro' in st.session_state:
            del st.session_state['personas_cuadro']
        if 'personas_pasan' in st.session_state:
            del st.session_state['personas_pasan']
        st.session_state.current_page = 'editar_torneo'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener participantes existentes si estamos editando
    participantes_existentes = []
    if categoria:
        participantes_data = db.obtener_participantes(categoria['id'])
        participantes_existentes = [p['nombre'] for p in participantes_data]
    
    # Campo de participantes FUERA del formulario para actualización en tiempo real
    st.subheader("👥 Participantes")
    
    participantes_text = st.text_area(
        "Lista de Participantes (uno por línea)",
        value="\n".join(participantes_existentes),
        height=200,
        help="Escribe el nombre de cada participante en una línea separada",
        key="participantes_input"
    )
    
    # Contador en tiempo real
    participantes_actuales = [p.strip() for p in participantes_text.split('\n') if p.strip()]
    total_participantes = len(participantes_actuales)
    
    if total_participantes > 0:
        st.markdown(f"**👥 Participantes ingresados: {total_participantes}**")
    else:
        st.markdown("**👥 Participantes ingresados: 0**")
    
    # Configuración FUERA del formulario para actualización en tiempo real
    st.subheader("⚙️ Configuración de Cuadros")
    
    # Valores por defecto si estamos editando
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
    
    # Cálculos automáticos EN TIEMPO REAL
    if total_participantes > 0:
        cuadros_necesarios = (total_participantes + personas_por_cuadro - 1) // personas_por_cuadro
        participantes_en_llaves = cuadros_necesarios * personas_que_pasan
        
        # Información visual
        st.markdown("### 📊 Información de la Categoría")
        
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric(
                label="👥 Total Participantes",
                value=total_participantes
            )
        
        with col_info2:
            st.metric(
                label="🟦 Cuadros Necesarios",
                value=cuadros_necesarios
            )
        
        with col_info3:
            st.metric(
                label="🏆 Pasan a Llaves",
                value=participantes_en_llaves
            )
        
        # Validaciones EN TIEMPO REAL
        if total_participantes < personas_por_cuadro:
            st.warning(f"⚠️ Necesitas al menos {personas_por_cuadro} participantes para formar un cuadro")
        elif personas_que_pasan > personas_por_cuadro:
            st.error(f"❌ Las personas que pasan ({personas_que_pasan}) no pueden ser mayores que las personas por cuadro ({personas_por_cuadro})")
        else:
            st.success(f"✅ Configuración válida: {cuadros_necesarios} cuadro(s) con {personas_por_cuadro} personas cada uno")
    
    # Formulario solo para nombre y guardar
    with st.form("categoria_form"):
        # Solo el nombre en el formulario
        nombre_default = categoria['nombre'] if categoria else ""
        nombre_categoria = st.text_input("Nombre de la Categoría", value=nombre_default)
        
        submit = st.form_submit_button("💾 Guardar Categoría", type="primary")
        
        if submit and nombre_categoria:
            # Obtener valores de los campos externos
            participantes_text_final = st.session_state.get('participantes_input', '')
            participantes_lista = [p.strip() for p in participantes_text_final.split('\n') if p.strip()]
            personas_por_cuadro_final = st.session_state.get('personas_cuadro', 4)
            personas_que_pasan_final = st.session_state.get('personas_pasan', 2)
            
            # Validaciones antes de guardar
            if not nombre_categoria.strip():
                st.error("❌ El nombre de la categoría es obligatorio")
                return
            
            if len(participantes_lista) < personas_por_cuadro_final:
                st.error(f"❌ Necesitas al menos {personas_por_cuadro_final} participantes")
                return
            
            if personas_que_pasan_final > personas_por_cuadro_final:
                st.error(f"❌ Las personas que pasan no pueden ser mayor a las personas por cuadro")
                return
            
            # Calcular cantidad de cuadros automáticamente
            cantidad_cuadros = (len(participantes_lista) + personas_por_cuadro_final - 1) // personas_por_cuadro_final
            
            if categoria:
                # Actualizar categoría existente
                if db.actualizar_categoria(categoria['id'], nombre_categoria.strip(), cantidad_cuadros, personas_por_cuadro_final):
                    st.success("✅ Categoría actualizada exitosamente!")
                else:
                    st.error("❌ Error al actualizar la categoría")
            else:
                # Crear nueva categoría
                categoria_id = db.crear_categoria(torneo['id'], nombre_categoria.strip(), cantidad_cuadros, personas_por_cuadro_final)
                if categoria_id:
                    # Agregar participantes
                    for participante in participantes_lista:
                        db.agregar_participante(categoria_id, participante)
                    st.success("✅ Categoría creada exitosamente!")
                else:
                    st.error("❌ Error al crear la categoría")
            
            # Volver a la página anterior
            st.session_state.selected_category = None
            # Limpiar los campos del formulario después de guardar
            if 'participantes_input' in st.session_state:
                del st.session_state['participantes_input']
            if 'personas_cuadro' in st.session_state:
                del st.session_state['personas_cuadro']
            if 'personas_pasan' in st.session_state:
                del st.session_state['personas_pasan']
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