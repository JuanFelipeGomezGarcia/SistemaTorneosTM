import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias con diseño profesional"""
    
    # CSS para bracket horizontal tipo llave tradicional
    st.markdown("""
    <style>
    .tournament-bracket {
        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 20px 0;
        overflow-x: auto;
        gap: 50px;
    }
    .bracket-round {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        min-width: 200px;
        position: relative;
    }
    .round-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 15px;
        font-weight: bold;
        margin-bottom: 20px;
        font-size: 0.9em;
    }
    .match-container {
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        margin: 15px 0;
        position: relative;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .match-container:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .final-match {
        border-color: #ffd700;
        background: linear-gradient(135deg, #fff9c4 0%, #ffecb3 100%);
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
    }
    .player-slot {
        padding: 12px 15px;
        border-bottom: 1px solid #dee2e6;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .player-slot:last-child {
        border-bottom: none;
    }
    .player-slot:hover {
        background: #e3f2fd;
    }
    .winner-slot {
        background: #d4edda;
        color: #155724;
        font-weight: bold;
    }
    .champion-slot {
        background: #fff3cd;
        color: #856404;
        font-weight: bold;
    }
    .connector-line {
        position: absolute;
        right: -25px;
        top: 50%;
        width: 25px;
        height: 2px;
        background: #6c757d;
        transform: translateY(-1px);
    }
    .bracket-round:last-child .connector-line {
        display: none;
    }
    .bye-slot {
        background: #d1ecf1;
        color: #0c5460;
        text-align: center;
        padding: 20px 15px;
        font-weight: bold;
        border-radius: 8px;
    }
    .vs-indicator {
        text-align: center;
        font-size: 0.8em;
        color: #6c757d;
        font-weight: bold;
        padding: 5px 0;
        background: #f8f9fa;
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
    
    # Mostrar bracket horizontal tipo llave
    st.subheader("🎯 Bracket Eliminatorio")
    
    # Crear el bracket horizontal
    st.markdown('<div class="tournament-bracket">', unsafe_allow_html=True)
    
    # Generar cada ronda horizontalmente
    for ronda in range(1, num_rondas + 1):
        st.markdown('<div class="bracket-round">', unsafe_allow_html=True)
        
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
                    # Determinar ganador y clases CSS
                    if ronda == num_rondas:
                        # Final
                        campeon_key = f'campeon_{categoria["id"]}'
                        ganador = st.session_state.get(campeon_key)
                        match_class = 'match-container final-match'
                    else:
                        # Rondas anteriores
                        ganador = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                        match_class = 'match-container'
                    
                    # Clases para jugadores
                    if ronda == num_rondas:
                        j1_class = 'player-slot champion-slot' if ganador == jugador1 else 'player-slot'
                        j2_class = 'player-slot champion-slot' if ganador == jugador2 else 'player-slot'
                    else:
                        j1_class = 'player-slot winner-slot' if ganador == jugador1 else 'player-slot'
                        j2_class = 'player-slot winner-slot' if ganador == jugador2 else 'player-slot'
                    
                    # Crear el HTML del enfrentamiento
                    match_html = f'''
                    <div class="{match_class}">
                        <div class="{j1_class}">{jugador1}</div>
                        <div class="vs-indicator">VS</div>
                        <div class="{j2_class}">{jugador2}</div>
                        <div class="connector-line"></div>
                    </div>
                    '''
                    
                    st.markdown(match_html, unsafe_allow_html=True)
                
                elif jugador1:  # Pase automático
                    bye_html = f'''
                    <div class="match-container">
                        <div class="bye-slot">🎯 {jugador1}<br><small>Pase automático</small></div>
                        <div class="connector-line"></div>
                    </div>
                    '''
                    st.markdown(bye_html, unsafe_allow_html=True)
                    
                    if ronda < num_rondas:
                        bracket[ronda + 1][i // 2] = jugador1
        
        st.markdown('</div>', unsafe_allow_html=True)  # Cerrar bracket-round
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar tournament-bracket
    
    # Controles interactivos debajo del bracket
    if puede_editar:
        st.markdown("---")
        st.subheader("🎮 Seleccionar Ganadores")
        
        # Crear columnas para los controles
        cols = st.columns(num_rondas)
        
        for ronda in range(1, num_rondas + 1):
            with cols[ronda - 1]:
                if ronda == num_rondas:
                    st.markdown("#### 🏆 FINAL")
                elif ronda == num_rondas - 1 and num_rondas > 2:
                    st.markdown("#### 🥉 SEMIFINAL")
                else:
                    st.markdown(f"#### Ronda {ronda}")
                
                participantes_ronda = bracket[ronda]
                
                for i in range(0, len(participantes_ronda), 2):
                    if i + 1 < len(participantes_ronda):
                        jugador1 = participantes_ronda[i]
                        jugador2 = participantes_ronda[i + 1]
                        
                        if jugador1 and jugador2:
                            match_key = f"match_r{ronda}_m{i//2}"
                            
                            if ronda == num_rondas:
                                # Final - seleccionar campeón
                                campeon_key = f'campeon_{categoria["id"]}'
                                
                                if st.button(f"👑 {jugador1}", key=f"{match_key}_j1", use_container_width=True):
                                    st.session_state[campeon_key] = jugador1
                                    st.rerun()
                                
                                if st.button(f"👑 {jugador2}", key=f"{match_key}_j2", use_container_width=True):
                                    st.session_state[campeon_key] = jugador2
                                    st.rerun()
                            else:
                                # Rondas anteriores
                                if st.button(f"✅ {jugador1}", key=f"{match_key}_j1", use_container_width=True):
                                    bracket[ronda + 1][i // 2] = jugador1
                                    st.rerun()
                                
                                if st.button(f"✅ {jugador2}", key=f"{match_key}_j2", use_container_width=True):
                                    bracket[ronda + 1][i // 2] = jugador2
                                    st.rerun()
                            
                            st.markdown("---")
    
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
                        border: 4px solid #FFD700; margin: 40px auto; max-width: 500px;
                        transform: scale(1.05);'>
                <h1 style='color: #333; margin: 0; text-shadow: 3px 3px 6px rgba(0,0,0,0.2); font-size: 2.5em;'>
                    🏆 CAMPEÓN 🏆
                </h1>
                <h2 style='color: #333; margin: 20px 0 0 0; font-size: 2em;'>{campeon_final}</h2>
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