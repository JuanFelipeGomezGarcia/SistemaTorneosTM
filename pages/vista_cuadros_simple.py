import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_simple_page():
    """Página simple para mostrar cuadros con enfrentamientos directos"""
    
    # Validar categoría seleccionada
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    # Verificar permisos de edición
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    st.title(f"🎯 {categoria['nombre']} - Vista Simple")
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
        st.warning("⚠️ Esta categoría necesita al menos 2 participantes")
        return
    
    # Generar cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    
    # Obtener resultados guardados
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    # Mostrar cada cuadro
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        st.subheader(f"🏓 Cuadro {cuadro_num}")
        
        # Crear enfrentamientos
        enfrentamientos = []
        for i in range(0, len(participantes_cuadro), 2):
            if i + 1 < len(participantes_cuadro):
                enfrentamientos.append((participantes_cuadro[i], participantes_cuadro[i + 1]))
        
        # Mostrar enfrentamientos
        for idx, (jugador1, jugador2) in enumerate(enfrentamientos):
            col1, col2, col3 = st.columns([2, 1, 2])
            
            # Buscar resultado guardado
            resultado_guardado = ""
            ganador_guardado = ""
            
            for partido in partidos_guardados:
                if (partido['cuadro_numero'] == cuadro_num and
                    partido['jugador1'] == jugador1 and
                    partido['jugador2'] == jugador2):
                    resultado_guardado = partido['resultado']
                    ganador_guardado = partido['ganador']
                    break
            
            with col1:
                color = "#27ae60" if ganador_guardado == jugador1 else "#333"
                st.markdown(f"<div style='color: {color}; font-weight: bold;'>{jugador1}</div>", unsafe_allow_html=True)
            
            with col2:
                if puede_editar:
                    resultado_key = f"resultado_{cuadro_num}_{idx}"
                    nuevo_resultado = st.selectbox(
                        "",
                        ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"],
                        index=0 if not resultado_guardado else ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"].index(resultado_guardado) if resultado_guardado in ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"] else 0,
                        key=resultado_key,
                        label_visibility="collapsed"
                    )
                    
                    # Guardar si cambió
                    if nuevo_resultado != resultado_guardado:
                        if nuevo_resultado == "":
                            if resultado_guardado:
                                db.guardar_resultado_partido(
                                    categoria['id'],
                                    cuadro_num,
                                    jugador1,
                                    jugador2,
                                    "",
                                    ""
                                )
                                st.rerun()
                        else:
                            partes = nuevo_resultado.split("-")
                            num1, num2 = int(partes[0]), int(partes[1])
                            ganador = jugador1 if num1 > num2 else jugador2
                            
                            db.guardar_resultado_partido(
                                categoria['id'],
                                cuadro_num,
                                jugador1,
                                jugador2,
                                nuevo_resultado,
                                ganador
                            )
                            st.rerun()
                else:
                    if resultado_guardado:
                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{resultado_guardado}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='text-align: center;'>vs</div>", unsafe_allow_html=True)
            
            with col3:
                color = "#27ae60" if ganador_guardado == jugador2 else "#333"
                st.markdown(f"<div style='color: {color}; font-weight: bold;'>{jugador2}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Botones finales
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    with col2:
        boton_text = "🏆 Ir a Llaves" if puede_editar else "🏆 Ver Llaves"
        if st.button(boton_text, type="primary", use_container_width=True):
            st.session_state.current_page = 'vista_llaves'
            st.rerun()

if __name__ == "__main__":
    vista_cuadros_simple_page()