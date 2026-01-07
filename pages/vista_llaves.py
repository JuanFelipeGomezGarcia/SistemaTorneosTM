import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias con selección visual de ganadores"""
    
    # CSS para el bracket visual
    st.markdown("""
    <style>
    .bracket-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin: 20px 0;
    }
    .round-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
    }
    .match-container {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        min-width: 300px;
    }
    .player-button {
        background: #f0f2f6;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 12px 20px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        font-weight: bold;
    }
    .player-button:hover {
        background: #e8f4fd;
        border-color: #1f77b4;
        transform: translateY(-2px);
    }
    .player-selected {
        background: #4CAF50 !important;
        color: white !important;
        border-color: #45a049 !important;
    }
    .vs-text {
        text-align: center;
        font-weight: bold;
        color: #666;
        margin: 10px 0;
    }
    .winner-indicator {
        background: #4CAF50;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        text-align: center;
        margin-top: 10px;
        font-weight: bold;
    }
    .round-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 25px;
        text-align: center;
        font-size: 1.2em;
        font-weight: bold;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
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
    
    # Obtener clasificados
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
            
        victorias = {p: 0 for p in participantes_cuadro}
        
        for partido in partidos:
            if partido['cuadro_numero'] == cuadro_num and partido['ganador']:
                if partido['ganador'] in victorias:
                    victorias[partido['ganador']] += 1
        
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
        next_power_of_2 = 2 ** num_rondas
        while len(clasificados) < next_power_of_2:
            clasificados.append(None)
        
        bracket = {1: clasificados.copy()}
        for ronda in range(2, num_rondas + 1):
            bracket[ronda] = [None] * (len(bracket[ronda - 1]) // 2)
        
        st.session_state[bracket_key] = bracket
    
    bracket = st.session_state[bracket_key]
    
    # Mostrar bracket visual
    st.subheader("🎯 Bracket Eliminatorio")
    
    # Crear columnas para cada ronda
    cols = st.columns(num_rondas)
    
    for ronda in range(1, num_rondas + 1):
        with cols[ronda - 1]:
            # Título de la ronda
            if ronda == num_rondas:
                titulo = "🏆 FINAL"
            elif ronda == num_rondas - 1 and num_rondas > 2:
                titulo = "🥉 SEMIFINAL"
            else:
                titulo = f"Ronda {ronda}"
            
            st.markdown(f'<div class="round-title">{titulo}</div>', unsafe_allow_html=True)
            
            participantes_ronda = bracket[ronda]
            
            # Mostrar enfrentamientos
            for i in range(0, len(participantes_ronda), 2):
                if i + 1 < len(participantes_ronda):
                    jugador1 = participantes_ronda[i]
                    jugador2 = participantes_ronda[i + 1]
                    
                    if jugador1 and jugador2:
                        match_key = f"match_r{ronda}_m{i//2}"
                        
                        st.markdown('<div class="match-container">', unsafe_allow_html=True)
                        
                        # Botones clickeables para seleccionar ganador
                        if puede_editar and ronda < num_rondas:
                            ganador_actual = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                            
                            # Jugador 1
                            if st.button(
                                jugador1, 
                                key=f"{match_key}_j1",
                                help="Click para seleccionar como ganador"
                            ):
                                bracket[ronda + 1][i // 2] = jugador1
                                st.rerun()
                            
                            st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)
                            
                            # Jugador 2
                            if st.button(
                                jugador2, 
                                key=f"{match_key}_j2",
                                help="Click para seleccionar como ganador"
                            ):
                                bracket[ronda + 1][i // 2] = jugador2
                                st.rerun()
                            
                            # Mostrar ganador seleccionado
                            if ganador_actual:
                                st.markdown(
                                    f'<div class="winner-indicator">✅ Ganador: {ganador_actual}</div>', 
                                    unsafe_allow_html=True
                                )
                        else:
                            # Solo mostrar (sin interacción)
                            st.write(f"**{jugador1}**")
                            st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)
                            st.write(f"**{jugador2}**")
                            
                            if ronda < num_rondas and bracket[ronda + 1][i // 2]:
                                ganador = bracket[ronda + 1][i // 2]
                                st.markdown(
                                    f'<div class="winner-indicator">✅ Ganador: {ganador}</div>', 
                                    unsafe_allow_html=True
                                )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    elif jugador1:  # Pase automático
                        st.info(f"🎯 **{jugador1}** pasa automáticamente")
                        if ronda < num_rondas:
                            bracket[ronda + 1][i // 2] = jugador1
    
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
        st.markdown("---")
        if st.button("💾 Guardar Bracket", type="primary"):
            st.session_state[bracket_key] = bracket
            st.success("✅ Bracket guardado exitosamente!")
            st.rerun()

if __name__ == "__main__":
    vista_llaves_page()
