import streamlit as st
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from database.db_operations import DatabaseOperations

class LoginPage:
    @staticmethod
    def render():
        UIComponents.header("🏓 Sistema de Torneos - Tenis de Mesa")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.subheader("Selecciona tu tipo de usuario")
            
            user_type = st.radio(
                "Tipo de usuario:",
                ["Administrador", "Competidor"],
                horizontal=True
            )
            
            if user_type == "Administrador":
                LoginPage._render_admin_form()
            else:
                LoginPage._render_competitor_form()
    
    @staticmethod
    def _render_admin_form():
        st.subheader("Iniciar Sesión - Administrador")
        
        with st.form("admin_login"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión")
            
            if submit:
                if not usuario or not password:
                    st.error("Por favor completa todos los campos")
                else:
                    db = DatabaseOperations()
                    if db.verificar_admin(usuario, password):
                        SessionManager.set('user_type', 'admin')
                        SessionManager.set('authenticated', True)
                        SessionManager.navigate('home')
                    else:
                        st.error("Usuario o contraseña incorrectos")
    
    @staticmethod
    def _render_competitor_form():
        if st.button("Continuar como Competidor"):
            SessionManager.set('user_type', 'competitor')
            SessionManager.set('authenticated', True)
            SessionManager.navigate('home')
