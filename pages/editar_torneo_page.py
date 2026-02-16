import streamlit as st
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from services.categoria_service import CategoriaService

class EditarTorneoPage:
    @staticmethod
    def render():
        torneo = SessionManager.get('selected_tournament')
        if not torneo:
            st.error("No hay torneo seleccionado")
            return
        
        st.title(f"📝 Editando: {torneo['nombre']}")
        st.write(f"📅 Fecha: {torneo['fecha']}")
        UIComponents.back_button(page='home')
        st.markdown("---")
        
        if st.button("➕ Agregar Nueva Categoría"):
            SessionManager.navigate('crear_categoria')
        
        st.markdown("---")
        EditarTorneoPage._render_categorias(torneo['id'])
    
    @staticmethod
    def _render_categorias(torneo_id):
        service = CategoriaService()
        categorias = service.obtener_categorias(torneo_id)
        
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
                            SessionManager.set('selected_category', categoria)
                            SessionManager.navigate('crear_categoria')
                
                st.markdown("---")
            
            if st.button("✅ Finalizar Creación del Torneo"):
                SessionManager.navigate('home')
        else:
            st.info("No hay categorías creadas. Agrega al menos una categoría para continuar.")
