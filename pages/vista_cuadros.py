import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Nueva vista de cuadros con selectbox"""
    
    st.success("✅ NUEVA VISTA DE CUADROS CARGADA")
    
    # Validaciones
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    # Permisos
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    # Header
    st.title(f"🎯 {categoria['nombre']}")
    st.write(f"Torneo: {torneo['nombre']}")
    
    # Debug
    st.info(f"🔧 Admin: {es_admin} | Estado: {torneo['estado']} | Puede editar: {puede_editar}")
    
    # Botón volver
    if st.button("← Volver a Categorías"):
        st.session_state.current_page = 'vista_categorias'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener datos
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    if len(participantes) < 2:
        st.warning("⚠️ Necesitas al menos 2 participantes")
        return
    
    # Generar cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    # Mostrar cada cuadro
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        st.subheader(f"🏓 Cuadro {cuadro_num}")
        
        # Enfrentamientos
        for i in range(len(participantes_cuadro)):
            for j in range(len(participantes_cuadro)):
                if i >= j:  # Solo mostrar la mitad superior de la matriz
                    continue
                
                jugador1 = participantes_cuadro[i]
                jugador2 = participantes_cuadro[j]
                
                # Buscar resultado guardado
                resultado_guardado = ""
                for partido in partidos_guardados:
                    if (partido['cuadro_numero'] == cuadro_num and
                        partido['jugador1'] == jugador1 and
                        partido['jugador2'] == jugador2):
                        resultado_guardado = partido['resultado']
                        break
                
                # Mostrar enfrentamiento
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.write(f"**{jugador1}**")
                
                with col2:
                    if puede_editar:
                        key = f"resultado_{cuadro_num}_{i}_{j}"
                        nuevo_resultado = st.selectbox(
                            "",
                            ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"],
                            index=0 if not resultado_guardado else ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"].index(resultado_guardado) if resultado_guardado in ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"] else 0,
                            key=key,
                            label_visibility="collapsed"
                        )
                        
                        # Guardar si cambió
                        if nuevo_resultado != resultado_guardado:
                            if nuevo_resultado == "":
                                if resultado_guardado:
                                    db.guardar_resultado_partido(categoria['id'], cuadro_num, jugador1, jugador2, "", "")
                                    st.rerun()
                            else:
                                partes = nuevo_resultado.split("-")
                                num1, num2 = int(partes[0]), int(partes[1])
                                ganador = jugador1 if num1 > num2 else jugador2
                                db.guardar_resultado_partido(categoria['id'], cuadro_num, jugador1, jugador2, nuevo_resultado, ganador)
                                st.rerun()
                    else:
                        if resultado_guardado:
                            st.write(f"**{resultado_guardado}**")
                        else:
                            st.write("vs")
                
                with col3:
                    st.write(f"**{jugador2}**")
        
        st.markdown("---")
    
    # Botones finales
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🏆 Ir a Llaves", type="primary", use_container_width=True):
            st.session_state.current_page = 'vista_llaves'
            st.rerun()

if __name__ == "__main__":
    vista_cuadros_page()