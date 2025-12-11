import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros, mostrar_cuadro, validar_cuadros_completos

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
    
    todos_resultados = {}
    cuadros_completos = 0
    
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) >= 2:
            st.markdown(f"### Cuadro {cuadro_num}")
            
            # Crear enfrentamientos
            enfrentamientos = []
            for i in range(0, len(participantes_cuadro), 2):
                if i + 1 < len(participantes_cuadro):
                    enfrentamientos.append((participantes_cuadro[i], participantes_cuadro[i + 1]))
            
            # Obtener resultados guardados
            partidos_guardados = db.obtener_partidos(categoria['id'])
            resultados_cuadro = {}
            
            for partido in partidos_guardados:
                if partido['cuadro_numero'] == cuadro_num:
                    key = f"{partido['jugador1']}_vs_{partido['jugador2']}"
                    resultados_cuadro[key] = {
                        'resultado': partido['resultado'],
                        'ganador': partido['ganador']
                    }
            
            # Mostrar enfrentamientos
            resultados_nuevos = {}
            partidos_completos = 0
            
            for idx, (jugador1, jugador2) in enumerate(enfrentamientos):
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.write(f"**{jugador1}**")
                
                with col2:
                    key_partido = f"{jugador1}_vs_{jugador2}"
                    resultado_guardado = resultados_cuadro.get(key_partido, {}).get('resultado', '')
                    
                    if puede_editar:
                        resultado_key = f"resultado_{cuadro_num}_{idx}"
                        resultado = st.selectbox(
                            "Resultado",
                            ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"],
                            index=["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"].index(resultado_guardado) if resultado_guardado else 0,
                            key=resultado_key
                        )
                        
                        if resultado:
                            if resultado in ["3-0", "3-1", "3-2"]:
                                ganador = jugador1
                            else:
                                ganador = jugador2
                            
                            resultados_nuevos[key_partido] = {
                                'resultado': resultado,
                                'ganador': ganador,
                                'jugador1': jugador1,
                                'jugador2': jugador2
                            }
                            partidos_completos += 1
                    else:
                        if resultado_guardado:
                            st.write(f"**{resultado_guardado}**")
                            partidos_completos += 1
                        else:
                            st.write("vs")
                
                with col3:
                    # Mostrar ganador si hay resultado
                    key_partido = f"{jugador1}_vs_{jugador2}"
                    ganador = resultados_cuadro.get(key_partido, {}).get('ganador', '')
                    if ganador == jugador2:
                        st.write(f"**{jugador2}** 🏆")
                    else:
                        st.write(jugador2)
            
            # Verificar si el cuadro está completo
            if partidos_completos == len(enfrentamientos):
                cuadros_completos += 1
                st.success(f"✅ Cuadro {cuadro_num} completado")
            
            todos_resultados[cuadro_num] = resultados_nuevos
            st.markdown("---")
    
    # Botones de acción
    if puede_editar:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Guardar Resultados"):
                # Guardar todos los resultados
                for cuadro_num, resultados in todos_resultados.items():
                    for partido, datos in resultados.items():
                        db.guardar_resultado_partido(
                            categoria['id'],
                            cuadro_num,
                            datos['jugador1'],
                            datos['jugador2'],
                            datos['resultado'],
                            datos['ganador']
                        )
                
                st.success("Resultados guardados exitosamente!")
                st.rerun()
        
        with col2:
            # Habilitar botón de llaves solo si todos los cuadros están completos
            if cuadros_completos == len([c for c in cuadros.values() if len(c) >= 2]):
                if st.button("🏆 Generar Llaves", key="generar_llaves_admin"):
                    st.session_state.current_page = 'vista_llaves'
                    st.rerun()
            else:
                st.button("🏆 Generar Llaves", disabled=True, help="Completa todos los cuadros primero", key="generar_llaves_disabled")
    
    else:
        # Solo mostrar botón de llaves para visualización
        if st.button("🏆 Ver Llaves", key="ver_llaves_competitor"):
            st.session_state.current_page = 'vista_llaves'
            st.rerun()

if __name__ == "__main__":
    vista_cuadros_page()