import streamlit as st
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from services.categoria_service import CategoriaService

class CrearCategoriaPage:
    @staticmethod
    def render():
        torneo = SessionManager.get('selected_tournament')
        categoria = SessionManager.get('selected_category')
        
        titulo = "✏️ Editar Categoría" if categoria else "➕ Crear Nueva Categoría"
        st.title(titulo)
        st.write(f"Torneo: {torneo['nombre']}")
        
        if st.button("← Volver"):
            SessionManager.set('selected_category', None)
            SessionManager.navigate('editar_torneo')
        
        st.markdown("---")
        CrearCategoriaPage._render_form(torneo, categoria)
    
    @staticmethod
    def _render_form(torneo, categoria):
        participantes_existentes = []
        if categoria:
            service = CategoriaService()
            participantes_data = service.obtener_participantes(categoria['id'])
            participantes_existentes = [p['nombre'] for p in participantes_data]
        
        st.subheader("👥 Participantes")
        participantes_text = st.text_area(
            "Lista de Participantes (uno por línea)",
            value="\n".join(participantes_existentes),
            height=200,
            key="participantes_input"
        )
        
        participantes_actuales = [p.strip() for p in participantes_text.split('\n') if p.strip()]
        st.markdown(f"**👥 Participantes ingresados: {len(participantes_actuales)}**")
        
        st.subheader("⚙️ Configuración de Cuadros")
        
        personas_default = categoria['personas_por_cuadro'] if categoria else 4
        
        col1, col2 = st.columns(2)
        with col1:
            personas_por_cuadro = st.number_input(
                "👥 Personas por Cuadro", 
                min_value=2, 
                max_value=8, 
                value=personas_default,
                key="personas_cuadro"
            )
        
        if len(participantes_actuales) > 0:
            cuadros_necesarios = (len(participantes_actuales) + personas_por_cuadro - 1) // personas_por_cuadro
            
            st.markdown("### 📊 Información de la Categoría")
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.metric("👥 Total Participantes", len(participantes_actuales))
            
            with col_info2:
                st.metric("🟦 Cuadros Necesarios", cuadros_necesarios)
        
        with st.form("categoria_form"):
            nombre_default = categoria['nombre'] if categoria else ""
            nombre_categoria = st.text_input("Nombre de la Categoría", value=nombre_default)
            
            submit = st.form_submit_button("💾 Guardar Categoría", type="primary")
            
            if submit:
                try:
                    participantes_lista = [p.strip() for p in st.session_state.get('participantes_input', '').split('\n') if p.strip()]
                    personas_por_cuadro_final = st.session_state.get('personas_cuadro', 4)
                    
                    service = CategoriaService()
                    service.crear_categoria(torneo['id'], nombre_categoria, personas_por_cuadro_final, participantes_lista)
                    
                    st.success("✅ Categoría creada exitosamente!")
                    SessionManager.set('selected_category', None)
                    SessionManager.navigate('editar_torneo')
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
