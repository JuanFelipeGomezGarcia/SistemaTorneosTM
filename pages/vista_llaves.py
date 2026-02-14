import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias estilo bracket tradicional"""
    
    # CSS para bracket con diseño tradicional
    st.markdown("""
    <style>
    .bracket-wrapper {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        overflow-x: auto;
        margin: 20px 0;
    }
    .bracket-container {
        display: flex;
        gap: 80px;
        justify-content: center;
        align-items: center;
    }
    .bracket-round {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        min-width: 220px;
    }
    .round-header {
        text-align: center;
        color: #2c3e50;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    }
    .match-box {
        background: white;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        overflow: hidden;
    }
    .player-item {
        padding: 15px 20px;
        border-bottom: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 16px;
    }
    .player-item:last-child {
        border-bottom: none;
    }
    .player-item:hover {
        background: #e3f2fd;
        transform: translateX(5px);
    }
    .player-winner {
        background: #4caf50;
        color: white;
        font-weight: bold;
    }
    .player-winner:hover {
        background: #45a049;
    }
    .vs-divider {
        text-align: center;
        padding: 5px;
        background: #f5f5f5;
        font-size: 12px;
        color: #999;
        font-weight: bold;
    }
    .final-box {
        border: 3px solid #ffd700;
        box-shadow: 0 6px 25px rgba(255, 215, 0, 0.4);
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
    
    # Botón para regenerar llaves
    if puede_editar:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Regenerar Llaves", help="Actualiza las llaves con los nuevos clasificados"):
                bracket_key = f'bracket_{categoria["id"]}'
                if bracket_key in st.session_state:
                    del st.session_state[bracket_key]
                campeon_key = f'campeon_{categoria["id"]}'
                if campeon_key in st.session_state:
                    del st.session_state[campeon_key]
                st.success("✅ Llaves regeneradas")
                st.rerun()
    
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
    
    # Procesar pases automáticos
    for ronda in range(1, num_rondas):
        participantes_ronda = bracket[ronda]
        for i in range(0, len(participantes_ronda), 2):
            if i + 1 < len(participantes_ronda):
                jugador1 = participantes_ronda[i]
                jugador2 = participantes_ronda[i + 1]
                
                # Si solo hay un jugador, pasa automáticamente
                if jugador1 and not jugador2:
                    bracket[ronda + 1][i // 2] = jugador1
                elif jugador2 and not jugador1:
                    bracket[ronda + 1][i // 2] = jugador2
    
    # Mostrar bracket
    st.markdown('<div class="bracket-wrapper">', unsafe_allow_html=True)
    
    # Crear columnas para cada ronda
    ronda_cols = st.columns(num_rondas)
    
    for ronda in range(1, num_rondas + 1):
        with ronda_cols[ronda - 1]:
            # Título de la ronda
            if ronda == num_rondas:
                st.markdown('<div class="round-header">🏆 FINAL</div>', unsafe_allow_html=True)
            elif ronda == num_rondas - 1 and num_rondas > 2:
                st.markdown('<div class="round-header">🥉 SEMIFINAL</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="round-header">Ronda {ronda}</div>', unsafe_allow_html=True)
            
            participantes_ronda = bracket[ronda]
            
            # Calcular espaciado inicial para centrar brackets verticalmente
            matches_in_round = len(participantes_ronda) // 2
            matches_in_prev_round = len(bracket[ronda - 1]) // 2 if ronda > 1 else 0
            
            # Agregar espaciado superior para centrar
            if ronda > 1:
                spacing_top = (2 ** (ronda - 1)) - 1
                for _ in range(spacing_top):
                    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
            
            # Mostrar enfrentamientos
            for i in range(0, len(participantes_ronda), 2):
                if i + 1 < len(participantes_ronda):
                    jugador1 = participantes_ronda[i]
                    jugador2 = participantes_ronda[i + 1]
                    
                    # Solo mostrar si ambos jugadores existen
                    if jugador1 and jugador2:
                        # Determinar ganador
                        if ronda == num_rondas:
                            campeon_key = f'campeon_{categoria["id"]}'
                            ganador = st.session_state.get(campeon_key)
                        else:
                            ganador = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                        
                        # Clase CSS para final
                        box_class = "match-box final-box" if ronda == num_rondas else "match-box"
                        
                        # Crear el match box con HTML
                        match_html = f'<div class="{box_class}">'
                        
                        if puede_editar:
                            # Mostrar como HTML pero usar botones de Streamlit
                            st.markdown(match_html, unsafe_allow_html=True)
                            
                            # Jugador 1
                            if ganador == jugador1:
                                st.markdown(f'<div class="player-item player-winner">✅ {jugador1}</div>', unsafe_allow_html=True)
                            else:
                                if st.button(jugador1, key=f"r{ronda}_m{i//2}_j1", use_container_width=True):
                                    if ronda == num_rondas:
                                        st.session_state[f'campeon_{categoria["id"]}'] = jugador1
                                    else:
                                        bracket[ronda + 1][i // 2] = jugador1
                                    st.rerun()
                            
                            st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)
                            
                            # Jugador 2
                            if ganador == jugador2:
                                st.markdown(f'<div class="player-item player-winner">✅ {jugador2}</div>', unsafe_allow_html=True)
                            else:
                                if st.button(jugador2, key=f"r{ronda}_m{i//2}_j2", use_container_width=True):
                                    if ronda == num_rondas:
                                        st.session_state[f'campeon_{categoria["id"]}'] = jugador2
                                    else:
                                        bracket[ronda + 1][i // 2] = jugador2
                                    st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            # Solo lectura
                            player1_class = "player-item player-winner" if ganador == jugador1 else "player-item"
                            player2_class = "player-item player-winner" if ganador == jugador2 else "player-item"
                            
                            match_html += f'''
                                <div class="{player1_class}">{"✅ " if ganador == jugador1 else ""}{jugador1}</div>
                                <div class="vs-divider">VS</div>
                                <div class="{player2_class}">{"✅ " if ganador == jugador2 else ""}{jugador2}</div>
                            </div>
                            '''
                            st.markdown(match_html, unsafe_allow_html=True)
                    
                    # Agregar espaciado vertical entre matches para centrar siguiente ronda
                    if i < len(participantes_ronda) - 2:
                        spacing_between = (2 ** ronda) - 1
                        for _ in range(spacing_between):
                            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar campeón final
    campeon_key = f'campeon_{categoria["id"]}'
    campeon_final = st.session_state.get(campeon_key)
    
    if campeon_final:
        st.balloons()
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%); 
                        border-radius: 25px; padding: 40px; text-align: center; 
                        box-shadow: 0 15px 40px rgba(255,215,0,0.4); 
                        border: 4px solid #FFD700; margin: 40px auto; max-width: 500px;'>
                <h1 style='color: #333; margin: 0; text-shadow: 3px 3px 6px rgba(0,0,0,0.2); font-size: 2.5em;'>
                    🏆 CAMPEÓN 🏆
                </h1>
                <h2 style='color: #333; margin: 20px 0 0 0; font-size: 2em;'>{campeon_final}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    vista_llaves_page()