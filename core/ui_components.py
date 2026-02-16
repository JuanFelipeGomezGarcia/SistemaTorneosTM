"""Componentes UI reutilizables"""
import streamlit as st

class UIComponents:
    @staticmethod
    def header(title, subtitle=None):
        st.title(title)
        if subtitle:
            st.write(subtitle)
        st.markdown("---")
    
    @staticmethod
    def back_button(text="← Volver", page=None, callback=None):
        if st.button(text, type="secondary"):
            if callback:
                callback()
            elif page:
                from core.session_manager import SessionManager
                SessionManager.navigate(page)
    
    @staticmethod
    def user_info():
        col1, col2 = st.columns([6, 1])
        with col2:
            from core.session_manager import SessionManager
            user_icon = "👨💼" if SessionManager.is_admin() else "🏓"
            user_text = "Administrador" if SessionManager.is_admin() else "Competidor"
            st.markdown(f"**{user_icon} {user_text}**")
            if st.button("Cerrar Sesión", type="secondary"):
                SessionManager.logout()
    
    @staticmethod
    def card(title, content, actions=None):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{title}**")
                st.write(content)
            with col2:
                if actions:
                    for action in actions:
                        action()
            st.markdown("---")
    
    @staticmethod
    def hide_sidebar():
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
        """, unsafe_allow_html=True)
