import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias estilo bracket tradicional"""
    
    # CSS para bracket tradicional con líneas conectoras
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
        gap: 60px;
        justify-content: flex-start;
        align-items: flex-start;
    }
    .bracket-round {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        position: relative;
    }
    .round-header {
        text-align: center;
        color: #2c3e50;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 20px;
        background: white;
        padding: 10px;
        border-radius: 10px;
    }
    .match-wrapper {
        position: relative;
        margin: 10px 0;
    }
    .match-box {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        overflow: hidden;
        position: relative;
        z-index: 2;
    }
    .player-item {
        padding: 12px 18px;
        border-bottom: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        font-size: 15px;
    }
    .player-item:last-child {
        border-bottom: none;
    }
    .player-item:hover {
        background: #e3f2fd;
    }
    .player-winner {
        background: #4caf50;
        color: white;
        font-weight: bold;
    }
    .vs-divider {
        text-align: center;
        padding: 4px;
        background: #f5f5f5;
        font-size: 11px;
        color: #999;
        font-weight: bold;
    }
    .final-box {
        border: 3px solid #ffd700;
        box-shadow: 0 6px 25px rgba(255, 215, 0, 0.4);
    }
    /* Líneas conectoras */
    .connector {
        position: absolute;
        right: -60px;
        width: 60px;
        height: 2px;
        background: #333;
        top: 50%;
        z-index: 1;
    }
    .connector-vertical {
        position: absolute;
        right: -60px;
        width: 2px;
        background: #333;
        z-index: 1;
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
    
    # Mostrar bracket con controles integrados
    st.markdown('<div class="bracket-wrapper"><div class="bracket-container">', unsafe_allow_html=True)
    
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
            
            # Calcular espaciado
            match_height = 100
            spacing = match_height * (2 ** (ronda - 1))
            
            for i in range(0, len(participantes_ronda), 2):
                if i + 1 < len(participantes_ronda):
                    jugador1 = participantes_ronda[i]
                    jugador2 = participantes_ronda[i + 1]
                    
                    if jugador1 and jugador2:
                        # Determinar ganador
                        if ronda == num_rondas:
                            campeon_key = f'campeon_{categoria["id"]}'
                            ganador = st.session_state.get(campeon_key)
                        else:
                            ganador = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                        
                        # Espaciado superior
                        if i > 0:
                            st.markdown(f'<div style="height: {spacing}px;"></div>', unsafe_allow_html=True)
                        elif ronda > 1:
                            initial_spacing = spacing // 2
                            st.markdown(f'<div style="height: {initial_spacing}px;"></div>', unsafe_allow_html=True)
                        
                        # Match box
                        box_class = "match-box final-box" if ronda == num_rondas else "match-box"
                        st.markdown(f'<div class="match-wrapper"><div class="{box_class}">', unsafe_allow_html=True)
                        
                        if puede_editar:
                            # Jugador 1 - botón clickeable
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
                            
                            # Jugador 2 - botón clickeable
                            if ganador == jugador2:
                                st.markdown(f'<div class="player-item player-winner">✅ {jugador2}</div>', unsafe_allow_html=True)
                            else:
                                if st.button(jugador2, key=f"r{ronda}_m{i//2}_j2", use_container_width=True):
                                    if ronda == num_rondas:
                                        st.session_state[f'campeon_{categoria["id"]}'] = jugador2
                                    else:
                                        bracket[ronda + 1][i // 2] = jugador2
                                    st.rerun()
                        else:
                            # Solo lectura
                            p1_class = "player-item player-winner" if ganador == jugador1 else "player-item"
                            p2_class = "player-item player-winner" if ganador == jugador2 else "player-item"
                            st.markdown(f'''
                                <div class="{p1_class}">{"✅ " if ganador == jugador1 else ""}{jugador1}</div>
                                <div class="vs-divider">VS</div>
                                <div class="{p2_class}">{"✅ " if ganador == jugador2 else ""}{jugador2}</div>
                            ''', unsafe_allow_html=True)
                        
                        # Cerrar match box y agregar conector
                        connector = '<div class="connector"></div>' if ronda < num_rondas else ''
                        st.markdown(f'</div>{connector}</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
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