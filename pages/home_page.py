import streamlit as st
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from services.torneo_service import TorneoService

class HomePage:
    @staticmethod
    def render():
        st.title("🏓 Torneos de Tenis de Mesa")
        UIComponents.user_info()
        st.markdown("---")
        
        if SessionManager.is_admin():
            if st.button("➕ Crear Nuevo Torneo"):
                SessionManager.navigate('crear_torneo')
            st.markdown("---")
        
        HomePage._render_torneos()
    
    @staticmethod
    def _render_torneos():
        st.subheader("Torneos Disponibles")
        
        service = TorneoService()
        torneos = service.obtener_torneos()
        
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
                        SessionManager.set('selected_tournament', torneo)
                        SessionManager.navigate('vista_categorias')
            
            st.markdown("---")
