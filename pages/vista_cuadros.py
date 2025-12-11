import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Página para mostrar y editar los cuadros de una categoría"""
    
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
    
    # Mostrar cuadros
    st.subheader("Cuadros de la Categoría")
    
    # Obtener resultados guardados
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) >= 2:
            st.markdown(f"### Cuadro {cuadro_num}")
            
            # Crear enfrentamientos
            enfrentamientos = []
            for i in range(0, len(participantes_cuadro), 2):
                if i + 1 < len(participantes_cuadro):
                    enfrentamientos.append((participantes_cuadro[i], participantes_cuadro[i + 1]))
            
            # Mostrar enfrentamientos
            for idx, (jugador1, jugador2) in enumerate(enfrentamientos):
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.write(f"**{jugador1}**")
                
                with col2:
                    # Buscar resultado guardado
                    resultado_guardado = ""
                    for partido in partidos_guardados:
                        if (partido['cuadro_numero'] == cuadro_num and 
                            partido['jugador1'] == jugador1 and 
                            partido['jugador2'] == jugador2):
                            resultado_guardado = partido['resultado']
                            break
                    
                    if puede_editar:
                        resultado_key = f"resultado_{cuadro_num}_{idx}_{jugador1}_{jugador2}"
                        opciones = ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"]
                        index_actual = opciones.index(resultado_guardado) if resultado_guardado in opciones else 0
                        
                        resultado = st.selectbox(
                            "Resultado",
                            opciones,
                            index=index_actual,
                            key=resultado_key
                        )
                        
                        # Guardar resultado automáticamente si cambia
                        if resultado and resultado != resultado_guardado:
                            ganador = jugador1 if resultado in ["3-0", "3-1", "3-2"] else jugador2
                            db.guardar_resultado_partido(
                                categoria['id'],
                                cuadro_num,
                                jugador1,
                                jugador2,
                                resultado,
                                ganador
                            )
                            st.rerun()
                    else:
                        if resultado_guardado:
                            st.write(f"**{resultado_guardado}**")
                        else:
                            st.write("vs")
                
                with col3:
                    st.write(f"**{jugador2}**")
            
            st.markdown("---")
    
    # Botón para ir a llaves (siempre activo)
    st.markdown("### Acciones")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Actualizar Página"):
            st.rerun()
    
    with col2:
        boton_text = "🏆 Ir a Llaves" if puede_editar else "🏆 Ver Llaves"
        if st.button(boton_text):
            st.session_state.current_page = 'vista_llaves'
            st.rerun()

if __name__ == "__main__":
    vista_cuadros_page()