"""Gestor centralizado del estado de sesión"""
import streamlit as st

class SessionManager:
    @staticmethod
    def init():
        defaults = {
            'user_type': None,
            'authenticated': False,
            'current_page': 'login',
            'selected_tournament': None,
            'selected_category': None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get(key, default=None):
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key, value):
        st.session_state[key] = value
    
    @staticmethod
    def clear():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    @staticmethod
    def navigate(page):
        st.session_state.current_page = page
        st.rerun()
    
    @staticmethod
    def is_authenticated():
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def is_admin():
        return st.session_state.get('user_type') == 'admin'
    
    @staticmethod
    def logout():
        SessionManager.clear()
        SessionManager.init()
        st.rerun()
