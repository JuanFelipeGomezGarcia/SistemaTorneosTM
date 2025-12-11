import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Página para mostrar y manejar las llaves eliminatorias"""
    
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    # Verificar permisos de edición
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    st.title(f"🏆 Llaves - {categoria['nombre']}")
    st.write(f"Torneo: {torneo['nombre']}")
    
    # Botón volver
    if st.button("← Volver a Cuadros"):
        st.session_state.current_page = 'vista_cuadros'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener ganadores de cuadros
    partidos = db.obtener_partidos(categoria['id'])
    ganadores_por_cuadro = {}
    
    for partido in partidos:
        cuadro = partido['cuadro_numero']
        if partido['ganador']:
            if cuadro not in ganadores_por_cuadro:
                ganadores_por_cuadro[cuadro] = []
            ganadores_por_cuadro[cuadro].append(partido['ganador'])
    
    # Obtener ganadores únicos por cuadro (los que más partidos ganaron)
    ganadores_cuadros = []
    for cuadro in sorted(ganadores_por_cuadro.keys()):
        ganadores = ganadores_por_cuadro[cuadro]
        # Contar victorias por jugador
        conteo_victorias = {}
        for ganador in ganadores:
            conteo_victorias[ganador] = conteo_victorias.get(ganador, 0) + 1
        
        # Obtener el jugador con más victorias
        if conteo_victorias:
            ganador_cuadro = max(conteo_victorias, key=conteo_victorias.get)
            ganadores_cuadros.append(ganador_cuadro)
    
    if len(ganadores_cuadros) < 2:
        st.warning("Se necesitan al menos 2 ganadores de cuadros para generar las llaves")
        return
    
    # Generar estructura de llaves
    num_participantes = len(ganadores_cuadros)
    num_rondas = math.ceil(math.log2(num_participantes)) if num_participantes > 1 else 1
    
    st.subheader(f"Llaves Eliminatorias ({num_participantes} participantes)")
    
    # Inicializar llaves en session_state si no existen
    if f'llaves_{categoria["id"]}' not in st.session_state:
        llaves = {}
        llaves[1] = ganadores_cuadros.copy()
        
        # Crear rondas vacías
        for ronda in range(2, num_rondas + 1):
            participantes_ronda_anterior = len(llaves[ronda - 1])
            llaves[ronda] = [None] * (participantes_ronda_anterior // 2)
        
        st.session_state[f'llaves_{categoria["id"]}'] = llaves
    
    llaves = st.session_state[f'llaves_{categoria["id"]}']
    
    # Mostrar llaves por ronda
    for ronda in range(1, num_rondas + 1):
        if ronda == num_rondas and len(llaves[ronda]) == 1:
            st.subheader(f"🏆 CAMPEÓN")
        else:
            st.subheader(f"Ronda {ronda}")
        
        participantes_ronda = llaves[ronda]
        
        if ronda == 1:
            # Primera ronda - enfrentamientos iniciales
            for i in range(0, len(participantes_ronda), 2):
                if i + 1 < len(participantes_ronda):
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    jugador1 = participantes_ronda[i]
                    jugador2 = participantes_ronda[i + 1]
                    
                    with col1:
                        if puede_editar:
                            ganador1_key = f"llave_r{ronda}_{i}"
                            ganador1 = st.checkbox(
                                jugador1, 
                                key=ganador1_key,
                                value=st.session_state.get(ganador1_key, False)
                            )
                            
                            # Si se selecciona este jugador, deseleccionar el otro
                            if ganador1 and st.session_state.get(f"llave_r{ronda}_{i+1}", False):
                                st.session_state[f"llave_r{ronda}_{i+1}"] = False
                                
                        else:
                            st.write(f"**{jugador1}**")
                    
                    with col2:
                        st.write("🆚")
                    
                    with col3:
                        if puede_editar:
                            ganador2_key = f"llave_r{ronda}_{i+1}"
                            ganador2 = st.checkbox(
                                jugador2, 
                                key=ganador2_key,
                                value=st.session_state.get(ganador2_key, False)
                            )
                            
                            # Si se selecciona este jugador, deseleccionar el otro
                            if ganador2 and st.session_state.get(f"llave_r{ronda}_{i}", False):
                                st.session_state[f"llave_r{ronda}_{i}"] = False
                        else:
                            st.write(f"**{jugador2}**")
                    
                    # Determinar ganador para la siguiente ronda
                    if puede_editar:
                        if ganador1:
                            if len(llaves) > ronda:
                                llaves[ronda + 1][i // 2] = jugador1
                        elif ganador2:
                            if len(llaves) > ronda:
                                llaves[ronda + 1][i // 2] = jugador2
                        else:
                            if len(llaves) > ronda:
                                llaves[ronda + 1][i // 2] = None
        
        else:
            # Rondas siguientes
            for i in range(0, len(participantes_ronda), 2):
                if i + 1 < len(participantes_ronda):
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    jugador1 = participantes_ronda[i]
                    jugador2 = participantes_ronda[i + 1]
                    
                    with col1:
                        if jugador1:
                            if puede_editar:
                                ganador1_key = f"llave_r{ronda}_{i}"
                                ganador1 = st.checkbox(
                                    jugador1, 
                                    key=ganador1_key,
                                    value=st.session_state.get(ganador1_key, False)
                                )
                                
                                if ganador1 and st.session_state.get(f"llave_r{ronda}_{i+1}", False):
                                    st.session_state[f"llave_r{ronda}_{i+1}"] = False
                            else:
                                st.write(f"**{jugador1}**")
                        else:
                            st.write("TBD")
                    
                    with col2:
                        if jugador1 and jugador2:
                            st.write("🆚")
                        else:
                            st.write("")
                    
                    with col3:
                        if jugador2:
                            if puede_editar:
                                ganador2_key = f"llave_r{ronda}_{i+1}"
                                ganador2 = st.checkbox(
                                    jugador2, 
                                    key=ganador2_key,
                                    value=st.session_state.get(ganador2_key, False)
                                )
                                
                                if ganador2 and st.session_state.get(f"llave_r{ronda}_{i}", False):
                                    st.session_state[f"llave_r{ronda}_{i}"] = False
                            else:
                                st.write(f"**{jugador2}**")
                        else:
                            st.write("TBD")
                    
                    # Determinar ganador para la siguiente ronda
                    if puede_editar and jugador1 and jugador2:
                        if st.session_state.get(f"llave_r{ronda}_{i}", False):
                            if len(llaves) > ronda:
                                llaves[ronda + 1][i // 2] = jugador1
                        elif st.session_state.get(f"llave_r{ronda}_{i+1}", False):
                            if len(llaves) > ronda:
                                llaves[ronda + 1][i // 2] = jugador2
                        else:
                            if len(llaves) > ronda:
                                llaves[ronda + 1][i // 2] = None
                
                elif len(participantes_ronda) % 2 == 1 and i < len(participantes_ronda):
                    # Jugador que pasa automáticamente
                    jugador = participantes_ronda[i]
                    if jugador:
                        st.write(f"**{jugador}** (Pasa automáticamente)")
                        if len(llaves) > ronda:
                            llaves[ronda + 1][i // 2] = jugador
        
        st.markdown("---")
    
    # Verificar si hay un campeón
    if num_rondas > 0 and llaves[num_rondas] and llaves[num_rondas][0]:
        campeon = llaves[num_rondas][0]
        st.success(f"🏆 **CAMPEÓN: {campeon}** 🏆")
        
        # Guardar el ganador en la base de datos
        if puede_editar:
            # Aquí podrías actualizar la categoría con el ganador
            pass
    
    # Botón guardar
    if puede_editar:
        if st.button("💾 Guardar Llaves"):
            # Actualizar las llaves en session_state
            st.session_state[f'llaves_{categoria["id"]}'] = llaves
            st.success("Llaves guardadas exitosamente!")
            st.rerun()

if __name__ == "__main__":
    vista_llaves_page()