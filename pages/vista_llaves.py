import streamlit as st
from database.db_operations import DatabaseOperations
import math
from collections import Counter

def vista_llaves_page():
    """Vista de llaves eliminatorias con selección de ganadores"""
    
    # Validaciones
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    st.title(f"🏆 Llaves - {categoria['nombre']}")
    st.write(f"Torneo: {torneo['nombre']}")
    
    if st.button("← Volver a Cuadros"):
        st.session_state.current_page = 'vista_cuadros'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener clasificados (2 primeros de cada cuadro)
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    from utils.tournament_utils import generar_cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos = db.obtener_partidos(categoria['id'])
    
    # Calcular clasificados
    clasificados = []
    for cuadro_num in sorted(cuadros.keys()):
        participantes_cuadro = cuadros[cuadro_num]
        if len(participantes_cuadro) < 2:
            continue
            
        # Contar victorias
        victorias = {}
        for participante in participantes_cuadro:
            victorias[participante] = 0
        
        for partido in partidos:
            if partido['cuadro_numero'] == cuadro_num and partido['ganador']:
                if partido['ganador'] in victorias:
                    victorias[partido['ganador']] += 1
        
        # Ordenar y tomar los 2 primeros
        jugadores_ordenados = sorted(participantes_cuadro, key=lambda x: victorias.get(x, 0), reverse=True)
        
        if len(jugadores_ordenados) >= 1:
            clasificados.append(jugadores_ordenados[0])
        if len(jugadores_ordenados) >= 2:
            clasificados.append(jugadores_ordenados[1])
    
    if len(clasificados) < 2:
        st.warning("⚠️ Se necesitan al menos 2 clasificados")
        return
    
    # Mostrar clasificados
    st.subheader(f"🏅 Clasificados ({len(clasificados)} jugadores)")
    cols = st.columns(min(4, len(clasificados)))
    for i, clasificado in enumerate(clasificados):
        with cols[i % len(cols)]:
            st.info(clasificado)
    
    st.markdown("---")
    
    # Generar estructura de bracket
    num_participantes = len(clasificados)
    num_rondas = math.ceil(math.log2(num_participantes)) if num_participantes > 1 else 1
    
    # Inicializar bracket
    bracket_key = f'bracket_{categoria["id"]}'
    if bracket_key not in st.session_state:
        # Completar con None si es necesario para potencia de 2
        next_power_of_2 = 2 ** num_rondas
        while len(clasificados) < next_power_of_2:
            clasificados.append(None)
        
        bracket = {1: clasificados.copy()}
        for ronda in range(2, num_rondas + 1):
            bracket[ronda] = [None] * (len(bracket[ronda - 1]) // 2)
        
        st.session_state[bracket_key] = bracket
    
    bracket = st.session_state[bracket_key]
    
    # Mostrar bracket con selección de ganadores
    st.subheader("🎯 Bracket Eliminatorio")
    
    for ronda in range(1, num_rondas + 1):
        if ronda == num_rondas:
            st.markdown("### 🏆 FINAL")
        elif ronda == num_rondas - 1 and num_rondas > 2:
            st.markdown("### 🥉 SEMIFINAL")
        else:
            st.markdown(f"### Ronda {ronda}")
        
        participantes_ronda = bracket[ronda]
        
        # Mostrar enfrentamientos
        for i in range(0, len(participantes_ronda), 2):
            if i + 1 < len(participantes_ronda):
                jugador1 = participantes_ronda[i]
                jugador2 = participantes_ronda[i + 1]
                
                if jugador1 and jugador2:
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        st.write(f"**{jugador1}**")
                    
                    with col2:
                        if puede_editar and ronda < num_rondas:
                            # Radio button para seleccionar ganador
                            ganador_key = f"ganador_r{ronda}_m{i//2}"
                            ganador = st.radio(
                                "Ganador",
                                [jugador1, jugador2],
                                key=ganador_key,
                                label_visibility="collapsed",
                                horizontal=True
                            )
                            
                            # Actualizar siguiente ronda
                            bracket[ronda + 1][i // 2] = ganador
                        else:
                            st.write("**VS**")
                    
                    with col3:
                        st.write(f"**{jugador2}**")
                    
                    # Mostrar quién pasó a la siguiente ronda
                    if ronda < num_rondas and bracket[ronda + 1][i // 2]:
                        ganador_siguiente = bracket[ronda + 1][i // 2]
                        st.success(f"➡️ Pasa: **{ganador_siguiente}**")
                
                elif jugador1:  # Pase automático
                    st.info(f"🎯 **{jugador1}** pasa automáticamente")
                    if ronda < num_rondas:
                        bracket[ronda + 1][i // 2] = jugador1
        
        st.markdown("---")
    
    # Mostrar campeón
    if num_rondas > 0 and bracket[num_rondas] and bracket[num_rondas][0]:
        campeon = bracket[num_rondas][0]
        st.balloons()
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%); 
                        border-radius: 20px; padding: 30px; text-align: center; 
                        box-shadow: 0 12px 35px rgba(255,215,0,0.4); 
                        border: 4px solid #FFD700; margin: 30px auto; max-width: 400px;'>
                <h1 style='color: #333; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                    🏆 CAMPEÓN 🏆<br>{campeon}
                </h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Botón guardar
    if puede_editar:
        if st.button("💾 Guardar Bracket", type="primary"):
            st.session_state[bracket_key] = bracket
            st.success("Bracket guardado exitosamente!")
            st.rerun()

if __name__ == "__main__":
    vista_llaves_page()
