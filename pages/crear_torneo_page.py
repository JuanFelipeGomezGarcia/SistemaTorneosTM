import streamlit as st
from datetime import datetime
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from services.torneo_service import TorneoService

class CrearTorneoPage:
    @staticmethod
    def render():
        UIComponents.header("➕ Crear Nuevo Torneo")
        UIComponents.back_button(page='home')
        
        with st.form("crear_torneo_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_torneo = st.text_input("Nombre del Torneo")
            
            with col2:
                fecha_torneo = st.date_input("Fecha del Torneo", value=datetime.now())
            
            submit = st.form_submit_button("Crear Torneo")
            
            if submit:
                try:
                    service = TorneoService()
                    torneo_id = service.crear_torneo(nombre_torneo, fecha_torneo)
                    
                    if torneo_id:
                        st.success("Torneo creado exitosamente!")
                        torneo = service.obtener_torneo(torneo_id)
                        SessionManager.set('selected_tournament', torneo)
                        SessionManager.navigate('editar_torneo')
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
