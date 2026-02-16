import streamlit as st
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from services.categoria_service import CategoriaService
from services.torneo_service import TorneoService

class VistaCategorias:
    @staticmethod
    def render():
        torneo = SessionManager.get('selected_tournament')
        if not torneo:
            st.error("No hay torneo seleccionado")
            return
        
        st.title(f"🏓 {torneo['nombre']}")
        st.write(f"📅 Fecha: {torneo['fecha']}")
        UIComponents.back_button(page='home')
        st.markdown("---")
        
        VistaCategorias._render_categorias(torneo)
    
    @staticmethod
    def _render_categorias(torneo):
        service = CategoriaService()
        categorias = service.obtener_categorias(torneo['id'])
        
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
                    participantes = service.obtener_participantes(categoria['id'])
                    st.write(f"Participantes: {len(participantes)}")
                
                with col4:
                    if st.button("Ver", key=f"ver_cat_{categoria['id']}"):
                        SessionManager.set('selected_category', categoria)
                        SessionManager.navigate('vista_cuadros')
            
            st.markdown("---")
        
        if SessionManager.is_admin() and torneo['estado'] == 'en_curso':
            torneo_service = TorneoService()
            if torneo_service.puede_finalizar(torneo['id']):
                if st.button("🏆 Terminar Torneo"):
                    if torneo_service.actualizar_estado(torneo['id'], 'finalizado'):
                        st.success("¡Torneo finalizado exitosamente!")
                        torneo['estado'] = 'finalizado'
                        SessionManager.set('selected_tournament', torneo)
                        st.rerun()
