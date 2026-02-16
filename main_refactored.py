import streamlit as st
from config import Config
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.crear_torneo_page import CrearTorneoPage
from pages.editar_torneo_page import EditarTorneoPage
from pages.crear_categoria_page import CrearCategoriaPage
from pages.vista_categorias_page import VistaCategorias
from pages.vista_cuadros import vista_cuadros_page
from pages.vista_llaves import vista_llaves_page

st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state="collapsed"
)

UIComponents.hide_sidebar()
SessionManager.init()

def main():
    if not SessionManager.is_authenticated():
        LoginPage.render()
        return
    
    page = SessionManager.get('current_page')
    
    pages = {
        'home': HomePage.render,
        'crear_torneo': CrearTorneoPage.render,
        'editar_torneo': EditarTorneoPage.render,
        'crear_categoria': CrearCategoriaPage.render,
        'vista_categorias': VistaCategorias.render,
        'vista_cuadros': vista_cuadros_page,
        'vista_llaves': vista_llaves_page,
    }
    
    render_func = pages.get(page, HomePage.render)
    render_func()

if __name__ == "__main__":
    main()
