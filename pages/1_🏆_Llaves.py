import streamlit as st
from database.db_operations import DatabaseOperations

def main():
    """Página independiente de llaves"""
    
    st.set_page_config(
        page_title="Llaves - Sistema de Torneos",
        page_icon="🏆",
        layout="wide"
    )
    
    st.title("🏆 Llaves Eliminatorias")
    
    db = DatabaseOperations()
    
    # Obtener todos los torneos
    torneos = db.obtener_torneos()
    
    if not torneos:
        st.info("No hay torneos disponibles")
        return
    
    # Selector de torneo
    torneo_nombres = [f"{t['nombre']} ({t['fecha']})" for t in torneos]
    torneo_seleccionado = st.selectbox("Selecciona un torneo:", torneo_nombres)
    
    if torneo_seleccionado:
        # Encontrar el torneo seleccionado
        torneo_idx = torneo_nombres.index(torneo_seleccionado)
        torneo = torneos[torneo_idx]
        
        # Obtener categorías del torneo
        categorias = db.obtener_categorias(torneo['id'])
        
        if not categorias:
            st.info("Este torneo no tiene categorías")
            return
        
        # Selector de categoría
        categoria_nombres = [cat['nombre'] for cat in categorias]
        categoria_seleccionada = st.selectbox("Selecciona una categoría:", categoria_nombres)
        
        if categoria_seleccionada:
            # Encontrar la categoría seleccionada
            categoria_idx = categoria_nombres.index(categoria_seleccionada)
            categoria = categorias[categoria_idx]
            
            # Simular el estado de sesión para la vista de llaves
            st.session_state.selected_tournament = torneo
            st.session_state.selected_category = categoria
            st.session_state.user_type = "competitor"  # Solo lectura
            
            # Importar y mostrar la vista de llaves
            from pages.vista_llaves import vista_llaves_page
            vista_llaves_page()

if __name__ == "__main__":
    main()