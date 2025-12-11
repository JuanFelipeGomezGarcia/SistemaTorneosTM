import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Página para mostrar y editar los cuadros de una categoría"""
    
    # Validar categoría seleccionada
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    # Verificar permisos de edición
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    st.title(f"🎯 {categoria['nombre']}")
    st.write(f"Torneo: {torneo['nombre']}")
    
    # Botón volver
    if st.button("← Volver a Categorías"):
        st.session_state.current_page = 'vista_categorias'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener participantes
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    if len(participantes) < 2:
        st.warning("Esta categoría necesita al menos 2 participantes para generar cuadros")
        return
    
    # Generar cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    
    # Obtener resultados guardados desde BD
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    st.subheader("Cuadros de la Categoría")
    
    # RECORRER CADA CUADRO
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        st.markdown(f"## 🟦 Cuadro {cuadro_num}")
        
        jugadores = participantes_cuadro
        
        # ======== GENERAR TABLA ROUND ROBIN ========
        
        # Encabezado
        cols = st.columns([1.5] + [1 for _ in jugadores])
        cols[0].write("*DEPORTISTA O EQUIPO*")
        for i, j in enumerate(jugadores):
            cols[i+1].write(f"*{i+1}*")
        
        # Filas
        for i, jugador_fila in enumerate(jugadores):
            cols = st.columns([1.5] + [1 for _ in jugadores])
            cols[0].write(f"*{jugador_fila}*")
            
            for j, jugador_col in enumerate(jugadores):
                
                # Celda diagonal (negra)
                if i == j:
                    cols[j+1].markdown(
                        "<div style='background:black; height:32px; border-radius:3px;'></div>",
                        unsafe_allow_html=True
                    )
                    continue
                
                # Buscar resultado guardado
                resultado_guardado = ""
                ganador_guardado = ""
                
                for partido in partidos_guardados:
                    if (
                        partido['cuadro_numero'] == cuadro_num and
                        partido['jugador1'] == jugador_fila and
                        partido['jugador2'] == jugador_col
                    ):
                        resultado_guardado = partido['resultado']
                        ganador_guardado = partido['ganador']
                        break
                
                # Celda editable si tiene permisos
                if puede_editar:
                    opciones = ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"]
                    index_actual = opciones.index(resultado_guardado) if resultado_guardado in opciones else 0
                    
                    key = f"rr_{cuadro_num}{i}{j}{jugador_fila}{jugador_col}"
                    
                    nuevo_resultado = cols[j+1].selectbox(
                        "",
                        opciones,
                        index=index_actual,
                        key=key
                    )
                    
                    # Guardar si cambió
                    if nuevo_resultado and nuevo_resultado != resultado_guardado:
                        ganador = jugador_fila if nuevo_resultado in ["3-0", "3-1", "3-2"] else jugador_col
                        
                        db.guardar_resultado_partido(
                            categoria['id'],
                            cuadro_num,
                            jugador_fila,
                            jugador_col,
                            nuevo_resultado,
                            ganador
                        )
                        st.rerun()
                
                # Solo mostrar resultados si NO tiene permisos
                else:
                    if resultado_guardado:
                        cols[j+1].write(f"*{resultado_guardado}*")
                    else:
                        cols[j+1].write("")
        
        st.markdown("---")
    
    # ======== BOTONES FINALES ========
    st.markdown("### Acciones")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Actualizar Página"):
            st.rerun()
    
    with col2:
        boton_text = "🏆 Ir a Llaves" if puede_editar else "🏆 Ver Llaves"
        if st.button(boton_text):
            st.session_state.current_page = 'vista_llaves'
            st.rerun()

if __name__ == "__main__":
    vista_cuadros_page()